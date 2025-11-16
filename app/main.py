import os
from pathlib import Path
from typing import Annotated, List, Union

from dotenv import find_dotenv, load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_mcp import FastApiMCP
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.auth import get_optional_auth, require_auth, session_store
from app.database import close_db, get_db, init_db
from app.markdown_parser import MarkdownTaskParser
from app.sync_service import sync_all_projects, sync_project
from app.schemas import (
    AuthStatusResponse,
    BulkTaskFromMarkdownRequest,
    BulkTaskResponse,
    EpicDetailResponse,
    EpicResponse,
    TaskCreateRequest,
    TaskResponse,
    TokenSetRequest,
    UserStoryDetailResponse,
    UserStoryResponse,
)
from app.taiga_client import TaigaClient, TaigaClientError

BASE_DIR = Path(__file__).resolve().parent.parent
DOTENV_PATH = BASE_DIR / ".env"
if DOTENV_PATH.exists():
    load_dotenv(DOTENV_PATH, override=True)
else:
    load_dotenv(find_dotenv(), override=True)

app = FastAPI(title="Taiga Task API")

# Configurar MCP Server
mcp = FastApiMCP(app)
mcp.mount()

# Configure Jinja2 templates
templates = Jinja2Templates(directory=str(Path(__file__).parent / "templates"))


def _load_env(variable: str) -> str:
    value = os.getenv(variable)
    if value is None or not value.strip():
        raise RuntimeError(f"Falta la variable de entorno requerida: {variable}")
    return value.strip()


def _build_taiga_client() -> TaigaClient:
    base_url = _load_env("TAIGA_BASE_URL")

    # Token viene de la sesión (session_store), NO del .env
    auth_token = get_optional_auth()

    token_ttl_raw = os.getenv("TAIGA_TOKEN_TTL", "82800")
    try:
        token_ttl = int(token_ttl_raw)
    except ValueError as exc:
        raise RuntimeError("TAIGA_TOKEN_TTL debe ser un entero") from exc

    return TaigaClient(
        base_url=base_url,
        username=None,  # No usar username/password
        password=None,  # No usar username/password
        auth_token=auth_token,
        token_ttl=token_ttl,
    )


@app.on_event("startup")
async def startup_event() -> None:
    # Initialize database
    await init_db()

    # Initialize Taiga client
    client = _build_taiga_client()
    await client.start()
    app.state.taiga_client = client


@app.on_event("shutdown")
async def shutdown_event() -> None:
    # Close Taiga client
    client: TaigaClient | None = getattr(app.state, "taiga_client", None)
    if client is not None:
        await client.close()

    # Close database connections
    await close_db()


def get_taiga_client() -> TaigaClient:
    client: TaigaClient | None = getattr(app.state, "taiga_client", None)
    if client is None:
        raise RuntimeError("El cliente de Taiga no está inicializado")
    return client


TaigaClientDep = Annotated[TaigaClient, Depends(get_taiga_client)]


@app.post("/tasks", response_model=TaskResponse)
async def create_task(payload: TaskCreateRequest, taiga_client: TaigaClientDep) -> TaskResponse:
    try:
        task = await taiga_client.create_task(
            project=payload.project,
            subject=payload.subject,
            user_story=payload.user_story,
            description=payload.description,
        )
    except TaigaClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return TaskResponse(**task)


@app.get("/epics", response_model=List[EpicResponse])
async def list_epics(
    project: Annotated[
        Union[int, str], Query(..., description="ID del proyecto (int, recomendado) o slug (str)")
    ],
    taiga_client: TaigaClientDep,
) -> List[EpicResponse]:
    """Lista todas las épicas de un proyecto.

    Normalmente se usa el ID del proyecto (ej: 3), no el slug.
    """
    try:
        epics = await taiga_client.list_epics(project=project)
    except TaigaClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return [EpicResponse(**epic) for epic in epics]


@app.get("/epics/{epic_id}", response_model=EpicDetailResponse)
async def get_epic(
    epic_id: int,
    taiga_client: TaigaClientDep,
    verbose: Annotated[
        bool, Query(description="Incluir detalles completos de US y tareas")
    ] = False,
    include_user_stories: Annotated[bool, Query(description="Incluir user stories")] = True,
    include_tasks: Annotated[bool, Query(description="Incluir tareas")] = False,
) -> EpicDetailResponse:
    """Obtiene el detalle de una épica con sus user stories y tareas.

    Por defecto trae solo títulos de user stories. Con verbose=true trae todos los detalles.
    """
    try:
        # Obtener épica base (reutilizando método existente)
        epic = await taiga_client.get_epic(epic_id)

        result = EpicDetailResponse(**epic)

        # Si se pide incluir user stories
        if include_user_stories:
            # Reutilizar método existente con filtro epic
            user_stories = await taiga_client.list_user_stories(
                project=epic["project"],
                titles_only=not verbose,  # Si verbose, traer detalles completos
                epic=epic_id,
            )

            result.user_stories = [UserStoryResponse(**us) for us in user_stories]
            result.total_user_stories = len(user_stories)

            # Si se pide incluir tareas
            if include_tasks:
                tasks_list = []
                for us in user_stories:
                    # Reutilizar método existente
                    tasks = await taiga_client.list_tasks_for_user_story(us["id"])
                    tasks_list.extend(tasks)

                result.tasks = [TaskResponse(**task) for task in tasks_list]
                result.total_tasks = len(tasks_list)

        return result

    except TaigaClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/project-map")
async def get_project_map(
    project: Annotated[Union[int, str], Query(..., description="ID o slug de proyecto")],
    taiga_client: TaigaClientDep,
    include_tasks: Annotated[bool, Query(description="Incluir tareas en el mapa")] = True,
) -> dict:
    """Retorna mapa completo: Epics → User Stories → Tasks

    Usa el filtro epic del API para obtener las user stories de cada epic.
    Opcionalmente incluye las tareas de cada user story.
    """
    try:
        # Obtener epics
        epics = await taiga_client.list_epics(project=project)

        # Obtener user stories sin epic (pasando epic=None explícitamente no funciona,
        # así que obtenemos todas y filtramos las que no están en ningún epic)
        all_us = await taiga_client.list_user_stories(project=project, titles_only=False)

        # Track which user stories belong to epics
        us_in_epics = set()

        result = {
            "project": project,
            "total_epics": len(epics),
            "total_user_stories": 0,
            "epics": [],
            "user_stories_without_epic": [],
        }

        # Para cada epic, obtener sus user stories usando el filtro epic
        for epic in epics:
            epic_id = epic["id"]

            # Obtener user stories de este epic usando el filtro
            epic_user_stories = await taiga_client.list_user_stories(
                project=project, titles_only=False, epic=epic_id
            )

            # Track user story IDs
            for us in epic_user_stories:
                us_in_epics.add(us["id"])

            result["total_user_stories"] += len(epic_user_stories)

            # Si se pide incluir tasks, obtener las tasks de cada user story
            if include_tasks:
                for us in epic_user_stories:
                    tasks = await taiga_client.list_tasks_for_user_story(us["id"])
                    us["tasks"] = tasks
                    us["total_tasks"] = len(tasks)

            result["epics"].append(
                {
                    "id": epic["id"],
                    "ref": epic["ref"],
                    "subject": epic["subject"],
                    "color": epic.get("color"),
                    "total_user_stories": len(epic_user_stories),
                    "user_stories": epic_user_stories,
                }
            )

        # User stories sin epic son las que no aparecieron en ningún epic
        us_without_epic = [us for us in all_us if us["id"] not in us_in_epics]

        if include_tasks:
            for us in us_without_epic:
                tasks = await taiga_client.list_tasks_for_user_story(us["id"])
                us["tasks"] = tasks
                us["total_tasks"] = len(tasks)

        result["user_stories_without_epic"] = us_without_epic
        result["total_user_stories"] += len(us_without_epic)

        return result

    except TaigaClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/user-stories", response_model=UserStoryResponse)
async def create_user_story(
    project: Annotated[Union[int, str], Query(description="ID o slug de proyecto")],
    subject: Annotated[str, Query(description="Título de la historia")],
    taiga_client: TaigaClientDep,
    description: str = None,
    tags: List[str] = None,
) -> UserStoryResponse:
    try:
        story = await taiga_client.create_user_story(
            project=project, subject=subject, description=description, tags=tags
        )
    except TaigaClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return UserStoryResponse(**story)


@app.get("/user-stories", response_model=List[UserStoryResponse])
async def list_user_stories(
    project: Annotated[Union[int, str], Query(..., description="ID o slug de proyecto")],
    taiga_client: TaigaClientDep,
    titles_only: Annotated[bool, Query(description="Retorna solo id y título")] = False,
    epic: Annotated[int | None, Query(description="Filtrar por ID de epic")] = None,
) -> List[UserStoryResponse]:
    try:
        stories = await taiga_client.list_user_stories(
            project=project, titles_only=titles_only, epic=epic
        )
    except TaigaClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return [UserStoryResponse(**story) for story in stories]


@app.get("/user-stories/{user_story_id}", response_model=UserStoryDetailResponse)
async def get_user_story(
    user_story_id: int,
    taiga_client: TaigaClientDep,
    include_tasks: Annotated[bool, Query(description="Incluir tareas de esta user story")] = False,
) -> UserStoryDetailResponse:
    """Obtiene el detalle de una user story con todos sus campos.

    Con include_tasks=true trae todas las tareas asociadas con full detalle.
    """
    try:
        story = await taiga_client.get_user_story(user_story_id)
        result = UserStoryDetailResponse(**story)

        if include_tasks:
            tasks = await taiga_client.list_tasks_for_user_story(user_story_id)
            result.tasks = [TaskResponse(**task) for task in tasks]
            result.total_tasks = len(tasks)

        return result
    except TaigaClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.patch("/user-stories/{user_story_id}", response_model=UserStoryResponse)
async def update_user_story(
    user_story_id: int,
    taiga_client: TaigaClientDep,
    description: str = None,
    version: int = 1,
) -> UserStoryResponse:
    try:
        story = await taiga_client.update_user_story(
            user_story_id=user_story_id, description=description, version=version
        )
    except TaigaClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return UserStoryResponse(**story)


@app.get("/user-stories/{user_story_id}/tasks", response_model=List[TaskResponse])
async def list_tasks_for_user_story(
    user_story_id: int, taiga_client: TaigaClientDep
) -> List[TaskResponse]:
    try:
        tasks = await taiga_client.list_tasks_for_user_story(user_story_id)
    except TaigaClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return [TaskResponse(**task) for task in tasks]


@app.post("/debug/cache/clear")
async def clear_cache(taiga_client: TaigaClientDep) -> dict:
    await taiga_client.reset_token_cache()
    state = taiga_client.debug_state()
    state["cache_cleared"] = True
    return state


@app.get("/auth", response_model=AuthStatusResponse)
async def get_auth_status() -> AuthStatusResponse:
    """
    GET /auth - Verifica el estado del token actual.

    Retorna información sobre si hay un token válido en la sesión
    e instrucciones para obtener y configurar uno si no existe.
    """
    token_info = session_store.get_token_info()

    if token_info and token_info["is_valid"]:
        return AuthStatusResponse(
            authenticated=True,
            message="Token válido encontrado en sesión",
            expires_at=token_info.get("expires_at"),
        )
    else:
        return AuthStatusResponse(
            authenticated=False,
            message="No hay token válido en la sesión",
            error=(
                "Para obtener tu token de Taiga: "
                "1. Inicia sesión en Taiga, "
                "2. Abre DevTools del navegador (F12), "
                "3. Ve a Application/Storage > Cookies, "
                "4. Copia el valor de 'auth-token', "
                "5. Envíalo via POST /auth con {\"token\": \"tu_token_aqui\"}"
            ),
        )


@app.post("/auth", response_model=AuthStatusResponse)
async def set_auth_token(payload: TokenSetRequest, taiga_client: TaigaClientDep) -> AuthStatusResponse:
    """
    POST /auth - Establece el token de autenticación para la sesión.

    El token se almacena en memoria (session_store) y se usa para todas las
    peticiones subsecuentes. No se persiste en .env ni en disco.

    Args:
        payload: Objeto con el token de Taiga

    Returns:
        Estado de autenticación con información del usuario si el token es válido

    Raises:
        HTTPException: Si el token es inválido
    """
    try:
        # Guardar token en session store
        session_store.set_token(payload.token)

        # Actualizar el token en el cliente de Taiga también
        await taiga_client.set_auth_token(payload.token)

        # Verificar que el token funciona
        result = await taiga_client.check_connection()

        return AuthStatusResponse(
            authenticated=True,
            user=result.get("user"),
            token_preview=taiga_client._mask_token(payload.token),
            expires_at=result.get("token_expires_at"),
            message="Token establecido correctamente en la sesión",
        )

    except TaigaClientError as exc:
        # Limpiar token inválido de la sesión
        session_store.clear()
        raise HTTPException(
            status_code=401, detail=f"Token inválido o expirado: {str(exc)}"
        ) from exc


@app.post("/sync")
async def sync_data(
    taiga_client: TaigaClientDep,
    db: Annotated[AsyncSession, Depends(get_db)],
    _token: Annotated[str, Depends(require_auth)],
    project: Annotated[
        Union[int, str, None],
        Query(description="ID o slug del proyecto a sincronizar. Si no se especifica, sincroniza todos"),
    ] = None,
) -> dict:
    """
    POST /sync - Sincroniza datos de Taiga a la base de datos local.

    Sincroniza proyectos, épicas, user stories, tareas y tags desde Taiga API
    a la base de datos local SQLite/PostgreSQL.

    Args:
        project: Opcional. ID o slug del proyecto a sincronizar.
                Si no se especifica, sincroniza todos los proyectos accesibles.

    Returns:
        Estadísticas de la sincronización (items creados/actualizados/errores)

    Requires:
        Token de autenticación válido (via POST /auth)
    """
    from app.sync_service import SyncStats

    stats = SyncStats()

    try:
        if project is None:
            # Sync all projects
            stats = await sync_all_projects(db, taiga_client)
        else:
            # Sync specific project
            await sync_project(db, taiga_client, project, stats)

        return {
            "message": "Sincronización completada",
            "project": project if project else "all",
            "statistics": stats.to_dict(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error durante la sincronización: {str(e)}",
        ) from e


@app.get("/table-map", response_class=HTMLResponse)
async def get_table_map(
    project: Annotated[
        Union[int, str],
        Query(..., description="ID o slug del proyecto a visualizar"),
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> HTMLResponse:
    """
    GET /table-map - Visualiza el mapeo completo de datos sincronizados en HTML.

    Genera una tabla interactiva mostrando la jerarquía:
    Epics → User Stories → Tasks

    Args:
        project: ID o slug del proyecto a visualizar

    Returns:
        Página HTML con tabla interactiva del mapeo completo

    Features:
        - Búsqueda en tiempo real
        - Filtros por estado (open/closed)
        - Secciones colapsables
        - Estadísticas del proyecto
        - User stories huérfanas (sin epic)
    """
    from sqlalchemy import func, select
    from sqlalchemy.orm import selectinload

    from app.models import Epic, Project, Task, UserStory

    # Get project from DB
    # Try to parse as int first (Taiga ID)
    try:
        project_id = int(project)
        db_project = await crud.get_project_by_taiga_id(db, project_id)
    except (ValueError, TypeError):
        # If not an int, treat as slug
        result = await db.execute(select(Project).where(Project.slug == str(project)))
        db_project = result.scalar_one_or_none()

    if not db_project:
        raise HTTPException(status_code=404, detail=f"Project '{project}' not found in database. Run POST /sync?project={project} first.")

    # Get epics with their user stories and tasks (with tags eagerly loaded)
    epics_result = await db.execute(
        select(Epic)
        .where(Epic.project_id == db_project.id)
        .options(
            selectinload(Epic.user_stories).selectinload(UserStory.tags),
            selectinload(Epic.user_stories).selectinload(UserStory.tasks).selectinload(Task.tags)
        )
        .order_by(Epic.ref.desc())
    )
    epics = list(epics_result.scalars().all())

    # Add total_tasks to each epic
    for epic in epics:
        epic.total_tasks = sum(len(us.tasks) for us in epic.user_stories)

    # Get orphan user stories (without epic) with tags eagerly loaded
    orphans_result = await db.execute(
        select(UserStory)
        .where(UserStory.project_id == db_project.id, UserStory.epic_id.is_(None))
        .options(
            selectinload(UserStory.tags),
            selectinload(UserStory.tasks).selectinload(Task.tags)
        )
        .order_by(UserStory.ref.desc())
    )
    orphan_user_stories = list(orphans_result.scalars().all())

    # Calculate statistics
    stats_result = await db.execute(
        select(
            func.count(Epic.id).label("epics"),
            func.count(UserStory.id).label("user_stories"),
            func.count(Task.id).label("tasks"),
        )
        .select_from(Epic)
        .outerjoin(UserStory, Epic.id == UserStory.epic_id)
        .outerjoin(Task, UserStory.id == Task.user_story_id)
        .where(Epic.project_id == db_project.id)
    )
    stats_row = stats_result.one()

    # Count total user stories including orphans
    total_us_result = await db.execute(
        select(func.count(UserStory.id))
        .where(UserStory.project_id == db_project.id)
    )
    total_us = total_us_result.scalar()

    # Count total tasks including orphan US tasks
    total_tasks_result = await db.execute(
        select(func.count(Task.id))
        .where(Task.project_id == db_project.id)
    )
    total_tasks = total_tasks_result.scalar()

    # Count tags
    from app.models import Tag
    tags_result = await db.execute(
        select(func.count(Tag.id))
        .where(Tag.project_id == db_project.id)
    )
    total_tags = tags_result.scalar()

    stats = {
        "epics": len(epics),
        "user_stories": total_us,
        "tasks": total_tasks,
        "tags": total_tags,
    }

    # Generate AI reorganization proposals
    from app.ai_reorganizer import AIReorganizer
    ai = AIReorganizer()
    analysis = ai.analyze_project(epics, orphan_user_stories)

    return templates.TemplateResponse(
        "table_map.html",
        {
            "request": {},  # Jinja2 requires request object
            "project": db_project,
            "epics": epics,
            "orphan_user_stories": orphan_user_stories,
            "stats": stats,
            "ai_analysis": analysis,
        },
    )


@app.get("/debug/state")
def debug_state(taiga_client: TaigaClientDep) -> dict:
    return taiga_client.debug_state()


@app.post("/debug/auth")
async def debug_auth(taiga_client: TaigaClientDep) -> dict:
    return await taiga_client.auth_diagnostics()


@app.get("/projects")
async def list_projects(taiga_client: TaigaClientDep) -> List[dict]:
    """Lista todos los proyectos accesibles."""
    try:
        return await taiga_client.list_projects()
    except TaigaClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/projects/{project_id}")
async def get_project(project_id: Union[int, str], taiga_client: TaigaClientDep) -> dict:
    """Obtiene detalle de un proyecto por ID o slug."""
    try:
        return await taiga_client.get_project(project_id)
    except TaigaClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/tasks")
async def list_tasks(
    taiga_client: TaigaClientDep,
    project: Annotated[Union[int, str, None], Query()] = None,
    user_story: Annotated[int | None, Query()] = None,
    status: Annotated[int | None, Query()] = None,
    assigned_to: Annotated[int | None, Query()] = None,
) -> List[dict]:
    """Lista tareas con filtros opcionales."""
    try:
        return await taiga_client.list_tasks(
            project=project,
            user_story=user_story,
            status=status,
            assigned_to=assigned_to,
        )
    except TaigaClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/tasks/{task_id}")
async def get_task(task_id: int, taiga_client: TaigaClientDep) -> dict:
    """Obtiene detalle de una tarea específica."""
    try:
        return await taiga_client.get_task(task_id)
    except TaigaClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.patch("/tasks/{task_id}")
async def update_task(
    task_id: int,
    taiga_client: TaigaClientDep,
    subject: Annotated[str | None, Query()] = None,
    description: Annotated[str | None, Query()] = None,
    status: Annotated[int | None, Query()] = None,
    assigned_to: Annotated[int | None, Query()] = None,
    version: Annotated[int | None, Query()] = None,
) -> dict:
    """Actualiza una tarea existente."""
    try:
        return await taiga_client.update_task(
            task_id=task_id,
            subject=subject,
            description=description,
            status=status,
            assigned_to=assigned_to,
            version=version,
        )
    except TaigaClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.delete("/tasks/{task_id}")
async def delete_task(task_id: int, taiga_client: TaigaClientDep) -> dict:
    """Elimina una tarea."""
    try:
        await taiga_client.delete_task(task_id)
        return {"deleted": True, "task_id": task_id}
    except TaigaClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/projects/{project_id}/task-statuses")
async def get_task_statuses(
    project_id: Union[int, str], taiga_client: TaigaClientDep
) -> List[dict]:
    """Obtiene los estados de tareas disponibles en un proyecto."""
    try:
        return await taiga_client.get_task_statuses(project_id)
    except TaigaClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/projects/{project_id}/userstory-statuses")
async def get_userstory_statuses(
    project_id: Union[int, str], taiga_client: TaigaClientDep
) -> List[dict]:
    """Obtiene los estados de historias de usuario disponibles en un proyecto."""
    try:
        return await taiga_client.get_userstory_statuses(project_id)
    except TaigaClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/projects/{project_id}/milestones")
async def get_project_milestones(
    project_id: Union[int, str], taiga_client: TaigaClientDep
) -> List[dict]:
    """Lista todos los sprints/milestones de un proyecto.

    Retorna información completa de cada milestone incluyendo:
    - id, name, slug
    - estimated_start, estimated_finish
    - closed, total_points, closed_points
    - user_stories asociadas
    """
    try:
        milestones = await taiga_client.list_milestones(project_id)
    except TaigaClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return milestones


@app.get("/projects/{project_id}/tags")
async def get_project_tags(project_id: Union[int, str], taiga_client: TaigaClientDep) -> dict:
    """Obtiene todas las etiquetas (tags) del proyecto con sus colores.

    Retorna un diccionario donde:
    - key: nombre de la etiqueta
    - value: código de color hexadecimal o null si no tiene color
    """
    try:
        tags = await taiga_client.get_project_tags(project_id)
    except TaigaClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return tags


@app.get("/docs/bulk-markdown-example")
async def get_bulk_markdown_example() -> dict:
    """
    Retorna un ejemplo de cómo crear tareas desde markdown.

    Incluye:
    - Formato del markdown esperado
    - Ejemplo de request completo
    - Explicación de conversión de referencias
    """
    return {
        "description": "Crea múltiples tareas en Taiga desde un documento markdown",
        "endpoint": "POST /tasks/bulk-from-markdown",
        "markdown_format": {
            "description": "Formato esperado del markdown",
            "example": """### 1. Título de la tarea

**Componente**: Backend - API

**Descripción**:
Descripción detallada de lo que hace la tarea.

**Criterios de aceptación**:
- Criterio 1
- Criterio 2
- Criterio 3

**Dependencias**: Tarea 1, HU #130, Sistema D3

---

### 2. Otra tarea

**Componente**: Frontend - UI

**Descripción**:
Otra descripción.

**Criterios de aceptación**:
- Criterio A
- Criterio B

**Dependencias**: Tarea 1""",
        },
        "request_example": {
            "markdown": "### 1. Modelo de datos\\n**Componente**: Backend\\n...",
            "project": "dai-declaracion-aduanera-integral",
            "user_story": 88,
            "taiga_base_url": "https://taiga.vuce-sidom.gob.ar",
        },
        "reference_conversion": {
            "description": "Referencias que se convierten automáticamente en links de Taiga",
            "examples": [
                {
                    "input": "Tarea 1",
                    "output": "[Tarea #1](https://taiga.../task/1)",
                },
                {
                    "input": "HU #130",
                    "output": "[HU #130](https://taiga.../us/130)",
                },
                {
                    "input": "US #88",
                    "output": "[US #88](https://taiga.../us/88)",
                },
                {"input": "#130", "output": "[#130](https://taiga.../us/130)"},
            ],
        },
        "automatic_tags": {
            "description": "Tags extraídos automáticamente del componente",
            "examples": [
                {"component": "Backend - API", "tags": ["backend", "api"]},
                {"component": "Frontend - UI", "tags": ["frontend", "ui"]},
                {"component": "Testing - E2E", "tags": ["testing"]},
                {
                    "component": "Backend - Integración",
                    "tags": ["backend", "integration"],
                },
            ],
        },
        "response_example": {
            "total_tasks": 2,
            "created_tasks": [
                {
                    "id": 150,
                    "ref": 150,
                    "subject": "Modelo de datos de configuración de menú",
                    "project": 3,
                    "user_story": 88,
                    "tags": ["backend"],
                },
                {
                    "id": 151,
                    "ref": 151,
                    "subject": "API de consulta de menú según permisos",
                    "project": 3,
                    "user_story": 88,
                    "tags": ["backend", "api"],
                },
            ],
            "errors": [],
        },
    }


@app.post("/tasks/bulk-from-markdown", response_model=BulkTaskResponse)
async def create_tasks_from_markdown(
    payload: BulkTaskFromMarkdownRequest, taiga_client: TaigaClientDep
) -> BulkTaskResponse:
    """
    Crea múltiples tareas desde un documento markdown y actualiza la descripción
    de la historia de usuario con los diagramas.

    El markdown debe tener el formato:
    ### 1. Título de la tarea
    **Componente**: Backend - API
    **Descripción**: ...
    **Criterios de aceptación**: ...
    **Dependencias**: ...
    """
    # Resolver project slug
    try:
        if isinstance(payload.project, str):
            project_slug = payload.project
        else:
            project_data = await taiga_client.get_project(payload.project)
            project_slug = project_data.get("slug", str(payload.project))
    except TaigaClientError as exc:
        raise HTTPException(status_code=400, detail=f"Proyecto no encontrado: {exc}") from exc

    # Obtener la historia de usuario para actualizar su descripción
    try:
        user_story = await taiga_client.get_user_story(payload.user_story)

        # Extraer la parte del markdown antes de "## Tareas Propuestas"
        # Esto incluye descripción, contexto y diagramas
        description_parts = payload.markdown.split("## Tareas Propuestas")
        if len(description_parts) > 0:
            us_description = description_parts[0].strip()

            # Actualizar la historia con los diagramas
            await taiga_client.update_user_story(
                user_story_id=payload.user_story,
                description=us_description,
                version=user_story.get("version"),
            )
    except TaigaClientError as exc:
        # No fallar si no se puede actualizar la historia, solo advertir
        print(f"Advertencia: No se pudo actualizar la historia: {exc}")

    # Parsear markdown
    parser = MarkdownTaskParser(taiga_base_url=payload.taiga_base_url)
    tasks_data = parser.parse_tasks(payload.markdown, project_slug)

    if not tasks_data:
        raise HTTPException(status_code=400, detail="No se encontraron tareas en el markdown")

    # Crear tareas
    created_tasks = []
    errors = []

    for idx, task_data in enumerate(tasks_data, 1):
        try:
            task = await taiga_client.create_task(
                project=payload.project,
                subject=task_data["subject"],
                user_story=payload.user_story,
                description=task_data["description"],
                # tags=task_data.get("tags"),  # Taiga no acepta tags en creación
            )
            created_tasks.append(TaskResponse(**task))
        except TaigaClientError as exc:
            errors.append(
                {
                    "task_number": idx,
                    "subject": task_data["subject"],
                    "error": str(exc),
                }
            )

    return BulkTaskResponse(total_tasks=len(tasks_data), created_tasks=created_tasks, errors=errors)
