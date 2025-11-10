# Configuración del MCP Server de Taiga para Claude Code

Este documento explica cómo configurar y usar el servidor MCP (Model Context Protocol) de Taiga con Claude Code.

## ¿Qué es MCP?

MCP (Model Context Protocol) es un protocolo abierto que permite a Claude Code conectarse con herramientas externas. Este proyecto expone todos los endpoints de la API de Taiga como herramientas MCP que Claude puede usar automáticamente.

## Instalación y Setup

### 1. Instalar dependencias

La integración MCP ya está instalada en el proyecto:

```bash
cd 02-util/taiga/taiga-fastapi-uv
uv sync
```

### 2. Configurar variables de entorno

Asegúrate de tener tu archivo `.env` configurado:

```bash
TAIGA_BASE_URL=https://your-taiga-instance.com/api/v1/
TAIGA_AUTH_TOKEN=your_token_here
TAIGA_TOKEN_TTL=82800
UVICORN_HOST=0.0.0.0
UVICORN_PORT=8000
```

### 3. Iniciar el servidor

```bash
uv run python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

O usando el script de desarrollo:

```bash
make dev
```

El servidor MCP estará disponible en: `http://localhost:8000/mcp`

## Configurar Claude Code

### Opción 1: Configuración local (recomendada para desarrollo)

Desde tu terminal, ejecuta:

```bash
claude mcp add --transport http taiga-local http://localhost:8000/mcp
```

### Opción 2: Configuración de proyecto (compartida con el equipo)

Crea o edita el archivo `.mcp.json` en la raíz del workspace:

```json
{
  "mcpServers": {
    "taiga-local": {
      "transport": "http",
      "url": "http://localhost:8000/mcp"
    }
  }
}
```

### Opción 3: Configuración de usuario (disponible en todos tus proyectos)

```bash
claude mcp add --scope user --transport http taiga http://localhost:8000/mcp
```

## Verificar la instalación

1. Lista los servidores MCP configurados:

```bash
claude mcp list
```

2. Verifica el servidor específico:

```bash
claude mcp get taiga-local
```

## Herramientas disponibles

Una vez configurado, Claude Code tendrá acceso automático a todas las operaciones de Taiga:

### Proyectos
- `GET /projects` - Listar todos los proyectos
- `GET /projects/{project_id}` - Obtener detalle de un proyecto

### User Stories
- `POST /user-stories` - Crear historia de usuario
- `GET /user-stories` - Listar historias de usuario
- `GET /user-stories/{user_story_id}` - Obtener detalle de una historia
- `PATCH /user-stories/{user_story_id}` - Actualizar historia
- `GET /user-stories/{user_story_id}/tasks` - Listar tareas de una historia

### Tareas
- `POST /tasks` - Crear tarea
- `GET /tasks` - Listar tareas con filtros
- `GET /tasks/{task_id}` - Obtener detalle de una tarea
- `PATCH /tasks/{task_id}` - Actualizar tarea
- `DELETE /tasks/{task_id}` - Eliminar tarea
- `POST /tasks/bulk-from-markdown` - Crear múltiples tareas desde markdown

### Epics
- `GET /epics` - Listar epics de un proyecto

### Estados
- `GET /projects/{project_id}/task-statuses` - Estados de tareas disponibles
- `GET /projects/{project_id}/userstory-statuses` - Estados de historias disponibles

### Debug
- `GET /debug/connection` - Verificar conexión con Taiga
- `GET /debug/state` - Estado del cliente
- `POST /debug/auth` - Diagnóstico de autenticación
- `POST /debug/cache/clear` - Limpiar caché de tokens

## Uso desde Claude Code

Una vez configurado, simplemente usa Claude Code normalmente. Claude detectará automáticamente cuándo necesita interactuar con Taiga y usará las herramientas MCP.

**Ejemplos de comandos:**

```
"Claude, crea una nueva user story en el proyecto dai-declaracion-aduanera-integral
titulada 'Implementar autenticación CF4'"

"Claude, lista todas las tareas de la user story #88"

"Claude, actualiza la tarea #150 cambiando su estado a completada"

"Claude, crea 5 tareas desde este markdown: [pegar markdown]"
```

## Seguridad y Autenticación

La autenticación con Taiga se maneja automáticamente usando:

1. El token de autenticación configurado en `.env`
2. La dependencia `TaigaClientDep` de FastAPI que gestiona el cliente autenticado
3. Todas las herramientas MCP heredan automáticamente esta autenticación

**No es necesario autenticar manualmente cada llamada desde Claude Code.**

## Troubleshooting

### El servidor MCP no responde

1. Verifica que el servidor esté corriendo:
```bash
curl http://localhost:8000/health
```

2. Verifica que el endpoint MCP esté disponible:
```bash
curl http://localhost:8000/mcp
```

### Claude Code no encuentra las herramientas

1. Verifica la configuración MCP:
```bash
claude mcp list
claude mcp get taiga-local
```

2. Reinicia Claude Code o recarga la configuración

### Errores de autenticación con Taiga

1. Verifica tu token:
```bash
curl http://localhost:8000/debug/auth
```

2. Limpia el caché de tokens:
```bash
curl -X POST http://localhost:8000/debug/cache/clear
```

## Deployment en producción

Para usar el MCP server en producción, necesitarás:

1. **Desplegar el servidor en un host accesible** (no localhost)
2. **Usar HTTPS** (requerido para MCP remoto)
3. **Configurar la URL completa** en Claude Code:

```bash
claude mcp add --transport http taiga-prod https://taiga-api.your-domain.com/mcp
```

### Ejemplo con Docker

```bash
cd 02-util/taiga/taiga-fastapi-uv
docker build -t taiga-mcp-server .
docker run -d -p 8000:8000 --env-file .env taiga-mcp-server
```

## Referencias

- Documentación MCP: https://code.claude.com/docs/en/mcp
- FastAPI-MCP: https://github.com/tadata-org/fastapi_mcp
- Documentación del proyecto Taiga: [README.md](../README.md)
