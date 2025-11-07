# Taiga FastAPI UV

Servicio FastAPI asíncrono que se autentica contra Taiga y permite crear tareas mediante un endpoint REST.

## Contexto del Proyecto

Este servicio es parte del proyecto **VUCE-SIDOM DAI** (Declaración Aduanera Informatizada), un sistema de digitalización de procesos aduaneros para Argentina bajo el préstamo BID 3869/OC-AR.

### Arquitectura del Sistema

```
Usuario → Load Balancer → Frontend (NextJS 15) → Backend (FastAPI) → MySQL 8.0
                                                      ↓
                                                  RabbitMQ
                                                      ↓
                                              Adapter (.NET x86)
                                                      ↓
                                              KIT Malvina/Maria
```

### Módulos del Sistema

- **D3 (Seguridad)**: Usuarios, autenticación vía Clave Fiscal ARCA, delegaciones CF4, roles y permisos
- **D4 (DAI)**: Operaciones IMEX - Creación y gestión de declaraciones aduaneras (módulo actual)
- **D5 (Catálogo)**: Mercaderías, NCM, productos y atributos
- **D6 (Búsqueda)**: Índices, consultas guardadas y reportes
- **D7-D8 (Documentos)**: LPCO, sobres digitales, adjuntos y firma digital

### Integraciones Externas

- **KIT Malvina/Maria**: Sistema legacy 32-bit para validaciones arancelarias y cálculo de tributos
- **VUCE Central**: Sistema central de Ventanilla Única de Comercio Exterior
- **TAD (ARCA)**: Sistema tributario y de autenticación
- **ARCA AFIP**: Autenticación vía Clave Fiscal

### Conceptos Clave

- **CF4**: CUIT de la empresa que el usuario está representando (no su propio CUIT)
- **Delegación**: Permiso que tiene un usuario para operar en nombre de una empresa (CF4)
- **Delegación Activa**: CF4 seleccionado actualmente por el usuario en su sesión

### ⚠️ Información Pendiente (Bloqueantes)

Estos puntos requieren definición con VUCE/DGA para completar la implementación:

1. **Acceso a datos del KIT Maria**: Protocolo de comunicación, endpoints y formato de datos
2. Catálogo completo de tipos de eventos para notificaciones
3. Diagrama de transición entre estados de operaciones
4. Matriz completa de permisos por rol
5. Política de retención de notificaciones históricas

## Índice

- [Contexto del Proyecto](#contexto-del-proyecto)
- [Flujo de Operaciones DAI](#flujo-de-operaciones-dai)
- [Requisitos previos](#requisitos-previos)
- [Configuración](#configuración)
- [Solución de Problemas de Autenticación](#solución-de-problemas-de-autenticación)
- [Instalación y Ejecución](#instalación-de-dependencias)
- [Endpoints Disponibles](#endpoint-disponible)
- [Recursos Adicionales](#recursos-adicionales)

## Flujo de Operaciones DAI

El módulo D4 implementa el flujo completo de declaraciones aduaneras:

### 1. Dashboard y Navegación
- Visualización de operaciones agrupadas por estado
- Notificaciones personales y operacionales (por CF4)
- Menú dinámico según permisos del usuario
- Cambio de CF4 con actualización automática del contexto

### 2. Creación de Operaciones
- **Manual**: Formulario paso a paso
- **Masiva**: Carga mediante archivo CSV

### 3. Carga de Información
1. **Pre-carátula**: Datos iniciales de la operación
2. **Carátula**: Información completa (varía según subrégimen)
3. **Ítems**: Mercaderías con posiciones arancelarias
4. **Subítems**: Detalle de cada mercadería
5. **Documentación**: Adjuntos y referencias

### 4. Validaciones
- Validaciones interactivas con KIT Malvina
- Preguntas dinámicas según tipo de operación
- Verificación de datos arancelarios

### 5. Oficialización
1. Liquidación de tributos
2. Generación de VEP (Volante Electrónico de Pago)
3. Oficialización final

### Estados de Operación

```
Borrador → En Carga → Validando → Observada → Lista → Oficializada → Pagada
                          ↓
                      Rechazada
```

### Notificaciones por Origen

- 🔵 **KIT Malvina**: Validaciones y cálculos arancelarios
- 🟢 **DAI Interno**: Eventos del sistema
- 🟠 **VUCE Central**: Coordinación interorganismos

## Relaciones entre Módulos

```
D3 (Seguridad)
  ↓ posee
D4 (Declaraciones) ← crea/modifica ← D3
  ↓ referencia
D5 (Catálogo) → indexa → D6 (Búsqueda)
  ↓ consulta                    ↓
D4 ← consulta ← D6              ↓
  ↓ genera                      ↓
D7-D8 (Documentos) ← almacena ← D6
```

### Dependencias Clave

- **D4 depende de D3**: Autenticación, permisos y delegaciones CF4
- **D4 depende de D5**: Catálogo de mercaderías y NCM
- **D4 depende de KIT Malvina**: Validaciones y cálculo de tributos (⚠️ bloqueante)
- **D4 integra con VUCE Central**: Notificaciones interorganismos
- **D6 indexa D4 y D5**: Búsquedas y reportes
- **D7-D8 almacena documentos de D4**: LPCO, adjuntos, firmas

## Requisitos previos

- Python 3.11 o superior
- [uv](https://github.com/astral-sh/uv) instalado globalmente

## Configuración

1. Copia `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```

2. **Configura la autenticación** (elige una opción):

### Opción 1: Token de API o Sesión (Recomendado)

#### Método A: Token de API desde la Interfaz Web

1. Ve a tu instancia de Taiga: https://tu-instancia-taiga.com
2. Inicia sesión con tu usuario y contraseña
3. Ve a tu perfil (click en tu avatar)
4. Ve a "Settings" o "Configuración"
5. Busca la sección "API" o "Application Tokens"
6. Genera un nuevo token de aplicación
7. Agrega el token al archivo `.env`:

```bash
TAIGA_AUTH_TOKEN=tu_token_de_api_aqui
```

> ** Importante**: Si no encuentras la opción "API" o "Application Tokens" en tu perfil, consulta con tu administrador de Taiga. Esta funcionalidad puede estar deshabilitada en tu instancia.

#### Método B: Token de Sesión del Navegador (Alternativo)

Si no tienes acceso a tokens de API en la interfaz web, puedes extraer el token de sesión desde las herramientas de desarrollador del navegador.

Sigue las instrucciones detalladas en la sección "Solución de Problemas de Autenticación" más abajo para obtener el token.

Una vez que tengas el token, agrégalo al archivo `.env`:

```bash
TAIGA_AUTH_TOKEN=tu_token_de_sesion_aqui
```

### Opción 2: Usuario y Contraseña

Si no puedes obtener un token de sesión:

```bash
TAIGA_USERNAME=tu_usuario
TAIGA_PASSWORD=tu_contraseña
```

## Solución de Problemas de Autenticación

### Problema Común: Credenciales no funcionan para la API

Si ves el error `"No active account found with the given credentials"`, significa que aunque puedas acceder a la interfaz web de Taiga, las credenciales de usuario/contraseña no funcionan para la API.

### Solución: Obtener Token de Autenticación

**Primero intenta el Método A** (Token de API desde la interfaz web). Si no tienes esa opción disponible, usa el **Método B** (Token de sesión del navegador).

#### Método B: Extraer Token de Sesión del Navegador

Sigue estos pasos para obtener un token válido:

#### 1. Abre las Herramientas de Desarrollador

- En Chrome/Edge: Presiona `F12` o `Ctrl+Shift+I`
- En Firefox: Presiona `F12` o `Ctrl+Shift+I`

#### 2. Configura la Captura de Red

1. Ve a la pestaña **"Network"** (Red)
2. Asegúrate de que esté grabando (botón rojo activo)
3. Filtra por **"XHR"** o **"Fetch"**

#### 3. Genera Tráfico de Red

- Recarga la página de Taiga (`F5`)
- O navega a cualquier sección del proyecto

#### 4. Encuentra el Token

1. Busca requests que vayan a `/api/v1/`
2. Click en cualquier request de la API
3. Ve a la pestaña **"Headers"** (Cabeceras)
4. En **"Request Headers"** busca:
   ```
   Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
   ```

#### 5. Copia y Configura el Token

1. **Copia solo el token** (la parte después de "Bearer ")
2. **Agrega el token al `.env`**:
   ```bash
   TAIGA_AUTH_TOKEN=tu_token_copiado_aqui
   ```
3. **Comenta las credenciales de usuario**:
   ```bash
   # TAIGA_USERNAME=tu_usuario
   # TAIGA_PASSWORD=tu_contraseña
   ```

![Ejemplo de interfaz de Taiga](util/taiga_token_example.jpg)

*La imagen muestra la interfaz de Taiga donde puedes acceder a las herramientas de desarrollador para extraer el token de autenticación*

#### 6. Verifica que Funciona

```bash
# Inicia el servidor
uv run uvicorn app.main:app --reload

# En otra terminal, prueba la autenticación
curl -X POST "http://localhost:8000/debug/auth"
```

Deberías ver:
```json
{
  "ok": true,
  "status_code": 200,
  "auth_method": "api_token",
  "token_cached": true
}
```

### Comandos de Diagnóstico

Si sigues teniendo problemas:

1. **Ejecuta el diagnóstico de autenticación**:
   ```bash
   curl -X POST "http://localhost:8000/debug/auth"
   ```

2. **Verifica el estado del cliente**:
   ```bash
   curl -X GET "http://localhost:8000/debug/state"
   ```

3. **Prueba la conexión**:
   ```bash
   curl -X GET "http://localhost:8000/debug/connection"
   ```

### Errores Comunes y Soluciones

| Error | Causa | Solución |
|-------|-------|----------|
| `"No active account found with the given credentials"` | Las credenciales de usuario/contraseña no funcionan para la API | Usa token de API (Método A) o token de sesión del navegador (Método B) |
| `"invalid_credentials"` | Usuario o contraseña incorrectos | Verifica que puedas iniciar sesión en la interfaz web |
| `"Se requiere autenticación"` | Token inválido o expirado | Obtén un nuevo token del navegador |
| `Error 404 en API` | URL base incorrecta | Asegúrate de que `TAIGA_BASE_URL` termine con `/` |
| `Connection refused` | Servidor no iniciado | Ejecuta `uv run uvicorn app.main:app --reload` |
| `Module not found` | Dependencias no instaladas | Ejecuta `uv sync` |

## Flujo de Trabajo de Desarrollo

### Opción 1: Script con uv (Recomendado)

#### Desarrollo Local (commits rápidos)

```bash
# Commit local rápido durante desarrollo
./scripts/update.sh --local "feat(auth): agregar validación"

# Ejecuta automáticamente:
# ✓ git add .
# ✓ Validaciones con uv (formateo, linting, tests)
# ✓ git commit con actualización de CHANGELOG.md
```

#### Push Remoto (con análisis)

```bash
# Análisis completo antes de push
./scripts/update.sh --remote

# El script:
# 1. Muestra diff de código
# 2. Muestra changelog temporal
# 3. Muestra commits locales
# 4. Opción para generar resumen con LLM
# 5. Commit formal + push

# Ideal para:
# - Antes de hacer push
# - Generar resumen profesional con LLM
# - Commits formales para el equipo
```

### Opción 2: Comandos Git Nativos

```bash
# 1. Hacer cambios en el código
# 2. Agregar archivos
git add .

# 3. Commit (todo se valida automáticamente)
git commit -m "feat(scope): descripción del cambio"

# Los hooks de git ejecutan automáticamente:
# ✓ Formateo de código (black, isort)
# ✓ Linting (flake8, pylint)
# ✓ Validación de secretos
# ✓ Tests (en main)
# ✓ Actualización de CHANGELOG.md
```

### Formato de Commits

Usa [Conventional Commits](https://www.conventionalcommits.org/):

```bash
feat(auth): agregar soporte para tokens de sesión
fix(client): corregir timeout de conexión
docs: actualizar guía de instalación
test: agregar tests para autenticación
```

**Tipos válidos:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`, `ci`, `build`

### Validaciones Automáticas

Los hooks de Git se ejecutan automáticamente en cada commit:

- **Pre-commit**: Formato, linting, validación de secretos
- **Prepare-commit-msg**: Actualización automática de CHANGELOG.md
- **Commit-msg**: Validación de formato Conventional Commits
- **Pre-push**: Tests obligatorios antes de push a `main`

### Omitir Tests en Desarrollo

En ramas de desarrollo (no `main`):

```bash
# Omitir tests en este commit
SKIP_TESTS=1 git commit -m "feat: trabajo en progreso"
```

**Nota:** Los tests son siempre obligatorios en `main`

### Comandos Útiles (Opcional)

El proyecto incluye un Makefile con comandos convenientes:

```bash
make dev          # Iniciar servidor
make test         # Ejecutar tests
make lint         # Linting
make format       # Formatear código
make ci           # Validación completa (simula CI)
```

### Reglas de Desarrollo

**Reglas automáticas (aplicadas por hooks):**
- ✅ Formato de código consistente (black, isort)
- ✅ Código sin errores de linting (flake8, pylint)
- ✅ Sin secretos o datos personales en commits
- ✅ Formato Conventional Commits obligatorio
- ✅ CHANGELOG.md actualizado automáticamente
- ✅ Tests obligatorios en `main`

**Flexibilidad en desarrollo:**
- En ramas feature/develop: Tests opcionales con `SKIP_TESTS=1`
- En `main`: Tests siempre obligatorios
- Changelog se actualiza automáticamente en cada commit

## Recursos Adicionales

### Documentación del Proyecto VUCE-SIDOM

- **`util/vuce-sidom-architecture.md`**: Arquitectura completa del sistema, módulos y stack tecnológico
- **`util/kit-maria-integration.md`**: Integración con KIT Malvina/Maria (⚠️ bloqueante crítico)
- **`util/system-overview.md`**: Visión general del sistema integrado

### Documentación de Desarrollo

- **Carpeta `util/`**: Contiene capturas de pantalla y guías adicionales para la configuración
- **Guía de desarrollo**: Ver `util/DEVELOPMENT.md` para documentación detallada de desarrollo
- **Herramientas de diagnóstico**: Usa los endpoints `/debug/*` para troubleshooting
- **Documentación de API**: Disponible en `http://localhost:8000/docs` cuando el servidor esté ejecutándose
- **Soporte de administrador**: Si no encuentras opciones de API en tu perfil, contacta al administrador de tu instancia de Taiga

### Para Desarrolladores y Modelos de IA

- **Archivo `.llms`**: Punto de entrada y reglas para modelos de IA
- **Contrato LLM-Humano**: Los LLMs crean documentación en `util/`, los humanos mantienen README.md
- **CHANGELOG.md**: Registro automático de cambios del proyecto
- **Guías de commits**: Ver `util/commit-guidelines.md` para formato de commits

### Documentación Privada

- **`util/llm-docs-proyect/`**: Documentación privada del autor (no commiteable)
  - Historias de Usuario D4
  - TASKs de ejemplo D3
  - Diagramas de arquitectura y modelo de datos

## Instalación y Configuración

### Instalación Rápida (Recomendado)

```bash
# Configurar entorno completo (dependencias + hooks + validaciones)
./scripts/setup-dev.sh
```

Este script instala:
- Dependencias de desarrollo
- Hooks de pre-commit automáticos
- Validaciones de código
- Sistema de changelog automático

### Instalación Manual

```bash
# 1. Instalar dependencias
uv sync --dev

# 2. Instalar hooks de Git
uv run pre-commit install
uv run pre-commit install --hook-type prepare-commit-msg
uv run pre-commit install --hook-type commit-msg
uv run pre-commit install --hook-type pre-push
```

## Ejecución en Desarrollo

### Iniciar Servidor

```bash
# Usando uv (recomendado)
uv run uvicorn app.main:app --reload

# El servidor estará disponible en:
# - API: http://localhost:8000
# - Documentación interactiva: http://localhost:8000/docs
```

### Ejecutar Tests

```bash
# Todos los tests
uv run pytest

# Con cobertura
uv run pytest --cov=app --cov-report=term-missing

# Solo tests unitarios
uv run pytest -m "not integration"
```

### Validaciones Manuales

```bash
# Ejecutar todas las validaciones pre-commit
uv run pre-commit run --all-files

# Formatear código
uv run black app/ tests/
uv run isort app/ tests/

# Linting
uv run flake8 app/
uv run pylint app/
```

El servicio quedará disponible en `http://0.0.0.0:8000/`.

Para usar la api se recomienda ver la documentación `http://0.0.0.0:8000/docs`.

## Endpoints Disponibles

### Gestión de Proyectos

#### Listar proyectos

`GET /projects`

```bash
curl "http://0.0.0.0:8000/projects"
```

Retorna todos los proyectos accesibles por el usuario autenticado.

### Gestión de Tareas

#### Crear tarea

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

### Depuración

- `POST /debug/cache/clear` limpia el token cacheado (fuerza nueva autenticación en el próximo request).
- `GET /debug/connection` verifica la conexión contra Taiga y devuelve el usuario autenticado y la expiración del token.
- `GET /debug/state` expone el estado actual del cliente (base URL normalizada, si hay token cacheado y el último response recibido).
- `POST /debug/auth` ejecuta el login y devuelve el status y payload exactamente como responde Taiga (ideal para diagnosticar credenciales).
