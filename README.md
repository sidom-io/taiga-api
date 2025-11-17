# Taiga FastAPI UV

Servicio FastAPI asíncrono para gestión completa de proyectos Taiga con interfaz web interactiva para visualización y edición de User Stories y Tasks.

## 🎯 Características Principales

### ✅ Funcionalidades Implementadas

- **Autenticación flexible**: Soporta tokens de API, tokens de sesión del navegador y credenciales usuario/contraseña
- **API REST completa**: CRUD de proyectos, épicas, user stories y tareas
- **Interfaz web interactiva** (`/table-map`):
  - Visualización jerárquica: Epic → User Story → Task
  - Editor markdown integrado con vista previa en tiempo real
  - Sincronización bidireccional con Taiga
  - Persistencia de drafts en localStorage
  - Gestión de tags visuales
  - Renderizado de diagramas Mermaid
- **Integración MCP**: Herramientas nativas para Claude Code
- **Sistema de sincronización**: Sync completo de proyectos desde Taiga a SQLite local
- **Control de versiones**: Manejo automático de versiones para evitar conflictos de concurrencia
- **Creación masiva**: Importación de tareas desde markdown

### 🚧 Funcionalidades Pendientes

> **Importante**: Las siguientes funcionalidades están identificadas como necesarias para completar el flujo de trabajo:

1. **Gestión de Épicas**
   - [ ] Crear épicas desde la interfaz web
   - [ ] Eliminar épicas
   - [ ] Sincronizar épica completa a Taiga (crear si no existe, validar nombre único)

2. **Gestión de Tareas desde Interfaz Web**
   - [ ] Crear nuevas tareas desde el modal de User Story
   - [ ] Modificar tareas existentes (título, descripción, estado)
   - [ ] Eliminar tareas

3. **Sincronización Avanzada**
   - [ ] Migrar épica completa a Taiga con un solo botón
   - [ ] Asignar automáticamente User Stories a la épica migrada
   - [ ] Validación de nombres únicos antes de crear épicas

4. **Mejoras de Interfaz**
   - [ ] Drag & drop para reorganizar User Stories y Tasks
   - [ ] Filtros y búsqueda en la vista de tabla
   - [ ] Edición inline de títulos

## 📋 Índice

- [Contexto del Proyecto](#contexto-del-proyecto)
- [Quick Start](#quick-start)
- [Configuración](#configuración)
- [Uso de la Interfaz Web](#uso-de-la-interfaz-web)
- [API Endpoints](#api-endpoints)
- [Integración MCP](#integración-mcp)
- [Desarrollo](#desarrollo)
- [Recursos Adicionales](#recursos-adicionales)

## 🏗️ Contexto del Proyecto

Este servicio es parte del proyecto **VUCE-SIDOM DAI** (Declaración Aduanera Informatizada), un sistema de digitalización de procesos aduaneros para Argentina bajo el préstamo BID 3869/OC-AR.

### Módulos del Sistema VUCE-SIDOM

- **D3 (Seguridad)**: Usuarios, autenticación vía Clave Fiscal ARCA, delegaciones CF4, roles y permisos
- **D4 (DAI)**: Operaciones IMEX - Creación y gestión de declaraciones aduaneras
- **D5 (Catálogo)**: Mercaderías, NCM (Nomenclatura Común del Mercosur), productos y atributos
- **D6 (Búsqueda)**: Índices, consultas guardadas y reportes
- **D7-D8 (Documentos)**: LPCO, sobres digitales, adjuntos y firma digital

### Integraciones Externas

- **KIT Malvina/Maria**: Sistema legacy 32-bit para validaciones arancelarias y cálculo de tributos
- **VUCE Central**: Sistema central de Ventanilla Única de Comercio Exterior
- **TAD (ARCA)**: Sistema tributario y de autenticación
- **ARCA AFIP**: Autenticación vía Clave Fiscal

Para más detalles sobre la arquitectura completa, ver [`util/vuce-sidom-architecture.md`](util/vuce-sidom-architecture.md).

## 🚀 Quick Start

### Requisitos Previos

- Python 3.11 o superior
- [uv](https://github.com/astral-sh/uv) instalado globalmente

### Instalación Rápida

```bash
# 1. Clonar el repositorio
cd /path/to/taiga-fastapi-uv

# 2. Configurar entorno completo
./scripts/setup-dev.sh

# 3. Configurar autenticación
cp .env.example .env
# Edita .env y agrega tu TAIGA_AUTH_TOKEN o credenciales

# 4. Iniciar servidor
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

**Acceder a la aplicación:**
- API Docs: http://localhost:8001/docs
- Interfaz Web: http://localhost:8001/table-map?project=vuce-sidom-dai

## ⚙️ Configuración

### Autenticación con Taiga

Edita el archivo `.env` y elige una de estas opciones:

#### Opción 1: Token de API (Recomendado)

```bash
TAIGA_BASE_URL=https://tu-instancia-taiga.com/
TAIGA_AUTH_TOKEN=tu_token_de_api_aqui
```

**Cómo obtener el token de API:**
1. Ve a tu instancia de Taiga
2. Inicia sesión
3. Ve a tu perfil → Settings → Application Tokens
4. Genera un nuevo token

#### Opción 2: Token de Sesión del Navegador

Si no tienes acceso a tokens de API:

1. Abre DevTools en tu navegador (F12)
2. Ve a la pestaña Network
3. Recarga Taiga
4. Busca un request a `/api/v1/`
5. En Headers, copia el valor de `Authorization: Bearer ...`
6. Agrega el token (solo la parte después de "Bearer ") al `.env`:

```bash
TAIGA_AUTH_TOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

#### Opción 3: Usuario y Contraseña

```bash
TAIGA_USERNAME=tu_usuario
TAIGA_PASSWORD=tu_contraseña
```

### Verificar Autenticación

```bash
curl -X POST "http://localhost:8001/debug/auth"
```

Respuesta esperada:
```json
{
  "ok": true,
  "status_code": 200,
  "auth_method": "api_token",
  "token_cached": true
}
```

Para más detalles sobre troubleshooting de autenticación, ver la sección completa en el README original.

## 🖥️ Uso de la Interfaz Web

### Acceso

```
http://localhost:8001/table-map?project=<project_slug_o_id>
```

### Funcionalidades de la Interfaz

#### 1. Visualización Jerárquica

La interfaz muestra la estructura completa del proyecto:

```
📚 Epic 1
  ├─ 📖 User Story #1
  │   ├─ ✅ Task 1.1
  │   └─ ✅ Task 1.2
  └─ 📖 User Story #2
      └─ ✅ Task 2.1

📚 Epic 2
  └─ 📖 User Story #3
```

#### 2. Editor de User Stories y Tasks

**Abrir editor:**
- Click en cualquier User Story o Task

**Tabs disponibles:**
- **Source**: Editor markdown (editable)
- **Vista Previa**: Renderizado en tiempo real del markdown
- **HTML**: HTML original de Taiga (actualizado al sincronizar)

**Acciones:**
- **💾 Guardar en Draft**: Persiste cambios en localStorage del navegador
- **🚀 Enviar a Taiga**: Sincroniza con Taiga y actualiza todos los tabs
- **🚀 Taiga** (botón superior): Abre el elemento en Taiga web

**Características:**
- ✅ Persistencia automática de drafts
- ✅ Carga automática de drafts al abrir modal
- ✅ Renderizado de diagramas Mermaid
- ✅ Vista previa en tiempo real
- ✅ Control de versiones automático (evita conflictos de concurrencia)
- ✅ Limpieza automática de drafts después de sincronizar

#### 3. Gestión de Tags

- Visualización de tags con colores
- Agregar tags existentes a User Stories
- Los tags se sincronizan automáticamente con Taiga

#### 4. Estados y Metadatos

- Indicadores visuales de estados (Borrador, En Progreso, Completado, etc.)
- Referencias (#42, #43) para navegación rápida
- IDs internos para debugging

### Ejemplo de Uso Típico

1. **Abrir proyecto**:
   ```
   http://localhost:8001/table-map?project=vuce-sidom-dai
   ```

2. **Editar una User Story**:
   - Click en el título de la User Story
   - Edita en el tab "Source"
   - Ve el preview en tiempo real en "Vista Previa"
   - Click en "💾 Guardar en Draft" (opcional, guarda local)
   - Click en "🚀 Enviar a Taiga" (sincroniza con servidor)

3. **Revisar cambios en Taiga**:
   - Click en "🚀 Taiga" (botón verde arriba a la derecha)
   - Se abre Taiga en nueva pestaña mostrando el elemento actualizado

## 📡 API Endpoints

### Gestión de Proyectos

```bash
# Listar proyectos
GET /projects

# Obtener detalle de proyecto
GET /projects/{project_id}

# Obtener estados, milestones, tags
GET /projects/{project_id}/task-statuses
GET /projects/{project_id}/userstory-statuses
GET /projects/{project_id}/milestones
GET /projects/{project_id}/tags
```

### Gestión de Épicas

```bash
# Listar épicas de un proyecto
GET /epics?project=<id_o_slug>

# Obtener detalle de épica con user stories y tareas
GET /epics/{epic_id}?verbose=true&include_user_stories=true&include_tasks=true

# Obtener mapa completo del proyecto (Epics → US → Tasks)
GET /project-map?project=<id>&include_tasks=true
```

### Gestión de User Stories

```bash
# Listar user stories
GET /user-stories?project=<id>&epic=<epic_id>

# Obtener detalle
GET /user-stories/{user_story_id}?include_tasks=true

# Crear user story
POST /user-stories
{
  "project": "project-slug",
  "subject": "Título de la historia",
  "description": "# Descripción en markdown",
  "tags": ["backend", "api"]
}

# Actualizar user story
PATCH /user-stories/{user_story_id}?description=...&version=<version>

# Listar tareas de una user story
GET /user-stories/{user_story_id}/tasks
```

### Gestión de Tareas

```bash
# Listar tareas
GET /tasks?project=<id>&user_story=<id>&status=<id>

# Obtener detalle
GET /tasks/{task_id}

# Crear tarea
POST /tasks
{
  "project": "project-slug",
  "subject": "Título de la tarea",
  "user_story": 42,
  "description": "Descripción opcional"
}

# Actualizar tarea
PATCH /tasks/{task_id}?description=...&version=<version>

# Crear tareas masivamente desde markdown
POST /tasks/bulk/from-markdown
{
  "project": "project-slug",
  "user_story": 42,
  "markdown_content": "# Lista de tareas\n- Tarea 1\n- Tarea 2"
}
```

### Sincronización

```bash
# Sincronizar todos los proyectos desde Taiga
POST /sync/projects

# Sincronizar un proyecto específico
POST /sync/projects/{project_id}
```

### Autenticación Dinámica

```bash
# Establecer bearer token sin reiniciar
POST /auth/token
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

# Verificar conexión y usuario autenticado
GET /debug/connection

# Estado del cliente
GET /debug/state

# Limpiar cache de autenticación
POST /debug/cache/clear
```

### Interfaz Web

```bash
# Visualizar proyecto completo con editor interactivo
GET /table-map?project=<slug_o_id>
```

Para ejemplos completos y parámetros detallados, ver la documentación interactiva en http://localhost:8001/docs

## 🔌 Integración MCP

Este proyecto incluye integración nativa con **Model Context Protocol (MCP)**, permitiendo que Claude Code acceda directamente a todas las funcionalidades de la API de Taiga como herramientas nativas.

### Quick Start MCP

```bash
# 1. Iniciar servidor
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001

# 2. Configurar Claude Code
claude mcp add --transport http taiga-local http://localhost:8001/mcp

# 3. Usar Claude normalmente
# Claude detectará automáticamente cuándo necesita interactuar con Taiga
```

**Documentación completa**: Ver [`util/MCP_SETUP.md`](util/MCP_SETUP.md)

## 🛠️ Desarrollo

### Estructura del Proyecto

```
taiga-fastapi-uv/
├── app/
│   ├── main.py              # FastAPI app principal
│   ├── taiga_client.py      # Cliente de API de Taiga
│   ├── crud.py              # Operaciones de base de datos
│   ├── models.py            # Modelos SQLAlchemy
│   ├── schemas.py           # Schemas Pydantic
│   ├── sync_service.py      # Servicio de sincronización
│   ├── markdown_parser.py   # Parser de markdown para tareas
│   └── templates/
│       └── table_map.html   # Interfaz web interactiva
├── tests/                   # Tests unitarios e integración
├── scripts/
│   ├── setup-dev.sh         # Setup completo del entorno
│   └── update.sh            # Helper para commits
├── alembic/                 # Migraciones de base de datos
├── util/                    # Documentación adicional
└── .env                     # Configuración (no commiteado)
```

### Comandos de Desarrollo

```bash
# Iniciar servidor en desarrollo
make dev                     # http://0.0.0.0:8001

# Tests
make test                    # Todos los tests con cobertura
make test-unit               # Solo tests unitarios

# Calidad de código
make lint                    # flake8 + pylint
make format                  # black + isort
make ci                      # Validación completa (simula CI)

# Commits
./scripts/update.sh --local "feat(api): descripción"  # Commit local
./scripts/update.sh --remote                           # Análisis + push
```

### Flujo de Trabajo Git

El proyecto usa **Conventional Commits** con hooks automáticos:

```bash
# Formato de commits
feat(scope): descripción     # Nueva funcionalidad
fix(scope): descripción      # Bug fix
docs: descripción            # Documentación
test: descripción            # Tests
```

**Tipos válidos**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`, `build`

**Validaciones automáticas** (hooks de Git):
- ✅ Formateo de código (black, isort)
- ✅ Linting (flake8, pylint)
- ✅ Detección de secretos
- ✅ Tests (obligatorios en `main`)
- ✅ Actualización automática de CHANGELOG.md

### Tests

```bash
# Todos los tests
uv run pytest

# Con cobertura (mínimo 80%)
uv run pytest --cov=app --cov-report=term-missing

# Solo unitarios (sin integración)
uv run pytest -m "not integration"

# Test específico
uv run pytest tests/test_client.py::test_authentication -v
```

### Base de Datos

```bash
# Crear migración
alembic revision --autogenerate -m "descripción"

# Aplicar migraciones
alembic upgrade head

# Rollback
alembic downgrade -1
```

## 📚 Recursos Adicionales

### Documentación del Proyecto

- **[`util/vuce-sidom-architecture.md`](util/vuce-sidom-architecture.md)**: Arquitectura completa del sistema VUCE-SIDOM
- **[`util/kit-maria-integration.md`](util/kit-maria-integration.md)**: Integración con KIT Malvina/Maria
- **[`util/d5-catalogo-documentacion.md`](util/d5-catalogo-documentacion.md)**: Documentación del módulo D5 (Catálogo)
- **[`util/system-overview.md`](util/system-overview.md)**: Visión general del sistema

### Documentación Técnica

- **[`util/MCP_SETUP.md`](util/MCP_SETUP.md)**: Configuración MCP para Claude Code
- **[`util/DEVELOPMENT.md`](util/DEVELOPMENT.md)**: Guía detallada de desarrollo
- **[`.llms`](.llms)**: Contrato LLM-Humano y reglas del proyecto
- **[`CHANGELOG.md`](CHANGELOG.md)**: Historial de cambios (auto-generado)

### Documentación Privada (Cache Local)

- **[`util/llm-docs-proyect/`](util/llm-docs-proyect/)**: Documentación privada del proyecto (no commiteada)
  - README con estado completo y métricas
  - Desgloses técnicos de historias de usuario
  - Diagramas DrawIO de flujos y modelo de datos
  - Snapshots JSON de datos de Taiga
  - Archivos para carga masiva

### API Interactiva

Una vez iniciado el servidor, accede a:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

### Soporte

- **Issues de GitHub**: Para reportar bugs o solicitar funcionalidades
- **Administrador de Taiga**: Si tienes problemas de permisos o configuración de la instancia

## 📄 Licencia

Este proyecto es parte del programa VUCE-SIDOM DAI financiado por BID 3869/OC-AR.

---

**Última actualización**: 2025-01-16

**Estado del Proyecto**:
- ✅ API REST completa funcional
- ✅ Interfaz web interactiva con editor markdown
- ✅ Sincronización bidireccional con Taiga
- ✅ Integración MCP para Claude Code
- 🚧 Gestión de épicas desde interfaz (pendiente)
- 🚧 Creación y edición de tareas desde interfaz (pendiente)
