# Taiga FastAPI UV

Servicio FastAPI asíncrono que se autentica contra Taiga y permite crear tareas mediante un endpoint REST.

## Requisitos previos

- Python 3.11 o superior
- [uv](https://github.com/astral-sh/uv) instalado globalmente

## Configuración

1. Copiá `.env.example` a `.env` y completá tus credenciales:
   ```bash
   cp .env.example .env
   ```
2. Ajustá `TAIGA_USERNAME` y `TAIGA_PASSWORD` en `.env`.

## Instalación de dependencias

Ejecutá:

```bash
uv sync
```

## Ejecución en desarrollo

```bash
uv run uvicorn app.main:app --reload
```

El servicio quedará disponible en `http://0.0.0.0:8000`.

## Endpoint disponible

### Crear tarea

`POST /tasks`

```bash
curl -X POST http://0.0.0.0:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "project": "sample-project-slug",
    "subject": "Nueva tarea",
    "user_story": 42,
    "description": "Descripción opcional"
  }'
```

```bash
curl -X POST http://0.0.0.0:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "project": 123,
    "subject": "Nueva tarea por ID"
  }'
```

La respuesta exitosa incluye `id`, `subject`, `project`, `user_story` y `ref`.

### Listar historias de usuario

`GET /user-stories?project=<id_o_slug>&titles_only=<true|false>`

```bash
curl "http://0.0.0.0:8000/user-stories?project=sample-project-slug&titles_only=true"
```

### Obtener detalle de historia de usuario

`GET /user-stories/{user_story_id}`

```bash
curl "http://0.0.0.0:8000/user-stories/42"
```

### Listar tareas de una historia

`GET /user-stories/{user_story_id}/tasks`

```bash
curl "http://0.0.0.0:8000/user-stories/42/tasks"
```
