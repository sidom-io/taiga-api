# API Documentation - taiga-fastapi-uv

## Code Statistics

- **app/main.py**: 740 líneas (27 endpoints)
- **app/schemas.py**: 128 líneas (9 schemas)
- **app/taiga_client.py**: 811 líneas (30+ métodos async)
- **Total**: 1,679 líneas

## Schemas (app/schemas.py)

### Task Schemas
- `TaskCreateRequest`: Payload para crear tarea (project, subject, user_story, description, status, tags)
- `TaskResponse`: Response de tarea con validación de tags (ConfigDict extra='allow')

### User Story Schemas
- `UserStoryResponse`: Response base con validación de tags
- `UserStoryDetailResponse`: Extiende UserStoryResponse + tasks + total_tasks

### Epic Schemas
- `EpicResponse`: Campos base (id, ref, subject, project, color, description, created_date, modified_date)
- `EpicDetailResponse`: Extiende EpicResponse + user_stories + tasks + totales

### Auth Schemas
- `TokenSetRequest`: Bearer token para autenticación dinámica
- `AuthStatusResponse`: Estado de autenticación (authenticated, user, token_preview, expires_at, error, message)

### Bulk Operations
- `BulkTaskFromMarkdownRequest`: Crear tareas desde markdown
- `BulkTaskResponse`: Resultado de creación masiva

## Endpoints (app/main.py)

### Epics (4 endpoints)
- `GET /epics` → List[EpicResponse] - Lista épicas de proyecto (param: project ID)
- `GET /epics/{epic_id}` → EpicDetailResponse - Detalle épica con verbose mode
  - Params: verbose, include_user_stories, include_tasks
- `GET /project-map` → dict - Mapa completo Epics → US → Tasks
  - Params: project, include_tasks

### User Stories (5 endpoints)
- `GET /user-stories` → List[UserStoryResponse] - Lista US (params: project, titles_only, epic)
- `GET /user-stories/{user_story_id}` → UserStoryDetailResponse - Detalle US + tasks opcionales
- `POST /user-stories` → UserStoryResponse - Crear US
- `PATCH /user-stories/{user_story_id}` → UserStoryResponse - Actualizar US
- `GET /user-stories/{user_story_id}/tasks` → List[TaskResponse] - Tareas de US

### Tasks (6 endpoints)
- `GET /tasks` → List[dict] - Lista tareas (filtros: project, user_story, status, assigned_to)
- `GET /tasks/{task_id}` → dict - Detalle de tarea
- `POST /tasks` → TaskResponse - Crear tarea
- `PATCH /tasks/{task_id}` → dict - Actualizar tarea
- `DELETE /tasks/{task_id}` → dict - Eliminar tarea
- `POST /tasks/bulk-from-markdown` → BulkTaskResponse - Crear tareas desde markdown

### Projects (5 endpoints)
- `GET /projects` → List[dict] - Lista proyectos
- `GET /projects/{project_id}` → dict - Detalle proyecto
- `GET /projects/{project_id}/task-statuses` → List[dict] - Estados de tareas
- `GET /projects/{project_id}/userstory-statuses` → List[dict] - Estados de US
- `GET /projects/{project_id}/milestones` → List[dict] - Milestones/sprints
- `GET /projects/{project_id}/tags` → dict - Tags con colores

### Auth & Debug (5 endpoints)
- `GET /debug/connection` → AuthStatusResponse - Verificar autenticación
- `POST /auth/token` → AuthStatusResponse - Establecer bearer token dinámico
- `GET /debug/state` → dict - Estado interno del cliente
- `POST /debug/auth` → dict - Diagnóstico de autenticación
- `POST /debug/cache/clear` → dict - Limpiar caché de tokens

### Documentation (1 endpoint)
- `GET /docs/bulk-markdown-example` → dict - Ejemplo de formato markdown para bulk create

## Key Features

### Tag Validation
Normaliza tags de Taiga que vienen como `[['backend', None], ['frontend', None]]` a lista plana usando `field_validator`

### Dynamic Authentication
POST /auth/token permite actualizar bearer token sin reiniciar servidor. Token se almacena en memoria.

### Verbose Mode
GET /epics/{epic_id}?verbose=true trae detalles completos de US y tareas. Default: solo títulos.

### Project Map
GET /project-map organiza estructura completa: Epics → User Stories → Tasks, incluyendo US sin epic.

### Bulk Operations
Crear múltiples tareas desde markdown con auto-extracción de tags desde componente.

## TaigaClient Methods (app/taiga_client.py)

### Principales métodos agregados
- `get_epic(epic_id)` - Línea 302-317
- `set_auth_token(token)` - Línea 421-429
- `list_milestones(project)` - Línea 761-778
- `get_project_tags(project)` - Línea 780-796

### Patrón de error handling
Todos los métodos usan try/except con TaigaClientError y _record_response() para debugging.
