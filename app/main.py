import os
from pathlib import Path
from typing import Annotated, List, Union

from dotenv import load_dotenv, find_dotenv
from fastapi import Depends, FastAPI, HTTPException, Query

from app.schemas import TaskCreateRequest, TaskResponse, UserStoryResponse
from app.taiga_client import TaigaClient, TaigaClientError

BASE_DIR = Path(__file__).resolve().parent.parent
DOTENV_PATH = BASE_DIR / ".env"
if DOTENV_PATH.exists():
    load_dotenv(DOTENV_PATH, override=True)
else:
    load_dotenv(find_dotenv(), override=True)

app = FastAPI(title="Taiga Task API")


def _load_env(variable: str) -> str:
    value = os.getenv(variable)
    if value is None or not value.strip():
        raise RuntimeError(f"Falta la variable de entorno requerida: {variable}")
    return value.strip()


def _build_taiga_client() -> TaigaClient:
    base_url = _load_env("TAIGA_BASE_URL")

    # Intentar obtener token de API primero
    auth_token = os.getenv("TAIGA_AUTH_TOKEN")

    # Si no hay token, usar usuario/contraseña
    username = None
    password = None
    if not auth_token:
        username = _load_env("TAIGA_USERNAME")
        password = _load_env("TAIGA_PASSWORD")

    token_ttl_raw = os.getenv("TAIGA_TOKEN_TTL", "82800")
    try:
        token_ttl = int(token_ttl_raw)
    except ValueError as exc:
        raise RuntimeError("TAIGA_TOKEN_TTL debe ser un entero") from exc

    return TaigaClient(
        base_url=base_url,
        username=username,
        password=password,
        auth_token=auth_token,
        token_ttl=token_ttl,
    )


@app.on_event("startup")
async def startup_event() -> None:
    client = _build_taiga_client()
    await client.start()
    app.state.taiga_client = client


@app.on_event("shutdown")
async def shutdown_event() -> None:
    client: TaigaClient | None = getattr(app.state, "taiga_client", None)
    if client is not None:
        await client.close()


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


@app.get("/user-stories", response_model=List[UserStoryResponse])
async def list_user_stories(
    project: Annotated[Union[int, str], Query(..., description="ID o slug de proyecto")],
    taiga_client: TaigaClientDep,
    titles_only: Annotated[bool, Query(description="Retorna solo id y título")] = False,
) -> List[UserStoryResponse]:
    try:
        stories = await taiga_client.list_user_stories(project=project, titles_only=titles_only)
    except TaigaClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    return [UserStoryResponse(**story) for story in stories]


@app.get("/user-stories/{user_story_id}", response_model=UserStoryResponse)
async def get_user_story(user_story_id: int, taiga_client: TaigaClientDep) -> UserStoryResponse:
    try:
        story = await taiga_client.get_user_story(user_story_id)
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


@app.get("/debug/connection")
async def debug_connection(taiga_client: TaigaClientDep) -> dict:
    try:
        return await taiga_client.check_connection()
    except TaigaClientError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/debug/state")
def debug_state(taiga_client: TaigaClientDep) -> dict:
    return taiga_client.debug_state()


@app.post("/debug/auth")
async def debug_auth(taiga_client: TaigaClientDep) -> dict:
    return await taiga_client.auth_diagnostics()
