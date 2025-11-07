# Punto de entrada

Esta carpeta almacena documentación y material de apoyo para diagnosticar la integración con el proyecto. Además, sirve como mapa rápido de la estructura del repositorio y contexto importante para modelos de IA y desarrolladores.

## Árbol del proyecto

```text
taiga-fastapi-uv/
├── .llms                          # Punto de entrada para LLMs (contrato)
├── .pre-commit-config.yaml        # Configuración pre-commit hooks
├── .gitlab-ci.yml                 # Pipeline CI/CD GitLab
├── Makefile                       # Comandos de desarrollo
├── CHANGELOG.md                   # Registro automático de cambios
├── README.md                      # Guía principal (punto de entrada humano)
├── pyproject.toml                 # Configuración del proyecto y dependencias
├── uv.lock                        # Resolución exacta de dependencias (uv)
│
├── app/                           # Código fuente de la aplicación
│   ├── __init__.py                # Marca el paquete y expone la app
│   ├── __main__.py                # Entry point para ejecución como módulo
│   ├── main.py                    # Aplicación FastAPI y rutas REST
│   ├── schemas.py                 # Modelos Pydantic para validación
│   ├── taiga_client.py            # Cliente asíncrono de Taiga API
│   └── markdown_parser.py         # Parser para carga bulk desde markdown
│
├── tests/                         # Suite de tests
│   ├── __init__.py
│   ├── conftest.py                # Fixtures compartidos de pytest
│   ├── test_main.py               # Tests de endpoints FastAPI
│   └── test_taiga_client.py       # Tests del cliente Taiga
│
├── scripts/                       # Scripts de automatización
│   ├── setup-dev.sh               # Instalación completa del entorno
│   ├── setup-git-hooks.sh         # Instalación de hooks de Git
│   ├── update.sh                  # Script principal de commit (local/remote)
│   ├── update-changelog.sh        # Actualización automática de CHANGELOG
│   ├── analyze-changes.sh         # Análisis de cambios para commits
│   └── actualizar_remoto.sh       # Script legacy de actualización
│
└── util/                          # Documentación técnica (territorio LLM)
    ├── README.md                  # Este archivo (mantenido por humanos)
    ├── DEVELOPMENT.md             # Guía completa de desarrollo
    ├── commit-guidelines.md       # Guías de commits y versionado
    ├── llm-workflow.md            # Flujo de trabajo con LLM para commits
    ├── project-status.md          # Estado actual del proyecto y métricas
    ├── ejemplo-desglose-tareas.md # Ejemplo real de desglose de HU
    ├── system-overview.md         # Visión general del sistema integrado
    ├── vuce-sidom-architecture.md # Arquitectura completa VUCE-SIDOM DAI
    ├── d5-catalogo-documentacion.md # Documentación módulo D5 (Catálogo)
    ├── kit-maria-integration.md   # Integración con KIT Malvina/Maria
    ├── taiga-devtools-example.md  # Cómo extraer tokens del navegador
    ├── troubleshooting-uv-python.md # Resolución de errores comunes
    ├── taiga_token_example.jpg    # Captura con headers de autorización
    │
    └── llm-docs-proyect/          # Documentación privada (en .gitignore)
        ├── README.md              # Contexto completo del proyecto VUCE-SIDOM
        ├── graficos.drawio.xml    # Diagramas DrawIO actualizados (DER completo)
        ├── historias-d4-faltantes.md
        ├── crear-historias-en-taiga.md
        ├── ejemplo-uso-bulk-api.md
        ├── TAIGA-DATA-README.md
        │
        ├── Desgloses técnicos de HU:
        ├── tareas-hu125-paso1-precaratula.md
        ├── tareas-hu126-carga-masiva-csv.md
        ├── tareas-hu26-paso4-validacion-docs.md
        ├── tareas-hu27-paso5-bultos.md
        ├── tareas-hu28-paso6-presupuesto.md
        ├── tareas-hu128-notif-historicas-mejoradas.md
        ├── tareas-hu129-menu-lateral.md
        ├── tareas-hu130-actualizacion-contextual.md
        ├── tareas-hu-pago-vep.md
        ├── tareas-hu-polizas-cauciones.md
        │
        ├── Archivos bulk para Taiga:
        ├── bulk-tareas-hu26.md
        ├── bulk-tareas-hu27.md
        ├── bulk-tareas-hu28.md
        ├── bulk-tareas-hu125.md
        ├── bulk-tareas-pago-vep.md
        ├── bulk-tareas-polizas-cauciones.md
        ├── bulk-tareas-oficializacion.md
        │
        └── Datos JSON de Taiga:
            ├── taiga-user-stories-dai.json
            ├── taiga-userstory-statuses.json
            ├── taiga-tasks-us*.json (múltiples archivos)
            └── llm-docs-proyect.tar.gz (backup)
```

## Archivos en esta carpeta

### Documentación Principal

- **`README.md`** - Este archivo (mantenido por humanos) - Punto de entrada y mapa del proyecto
- **`DEVELOPMENT.md`** - Guía completa de desarrollo con flujos de trabajo y comandos
- **`project-status.md`** - Estado actual del proyecto, métricas y progreso de HU

### Arquitectura y Diseño

- **`vuce-sidom-architecture.md`** - Arquitectura completa del proyecto VUCE-SIDOM DAI
- **`system-overview.md`** - Visión general del sistema integrado y módulos
- **`kit-maria-integration.md`** - Integración con KIT Malvina/Maria (bloqueante crítico)
- **`d5-catalogo-documentacion.md`** - Documentación completa del módulo D5 (Catálogo)
  - Modelo de datos: NCM, ITEM, SUBITEM, CATALOGO_CAMPO
  - Relaciones entre entidades y reglas de negocio
  - Casos de uso y validaciones
- **`ejemplo-desglose-tareas.md`** - Ejemplo real de cómo desglosar HU en tareas (HU #129)

### Guías de Desarrollo

- **`commit-guidelines.md`** - Guías de commits y versionado semántico
- **`llm-workflow.md`** - Flujo de trabajo con LLM para commits profesionales
- **`troubleshooting-uv-python.md`** - Resolución de errores comunes con uv y Python 3.13

### Configuración y Troubleshooting

- **`taiga-devtools-example.md`** - Cómo extraer tokens de autenticación del navegador
- **`taiga_token_example.jpg`** - Captura de pantalla con headers de autorización

### Documentación Privada

- **`llm-docs-proyect/`** - Carpeta con documentación privada del proyecto (contenido en .gitignore)
  - Contexto completo del proyecto VUCE-SIDOM
  - **graficos.drawio.xml**: Diagramas DrawIO actualizados con DER completo
  - Historias de Usuario D4 con desgloses técnicos
  - Datos JSON de Taiga (snapshots de HU y tareas)
  - Desgloses técnicos de historias de usuario
  - Archivos bulk para carga masiva en Taiga
  - Datos JSON exportados de Taiga
  - Ver `llm-docs-proyect/README.md` para índice completo

### Carpeta de Documentación Privada

La carpeta `llm-docs-proyect/` contiene documentación privada bajo autoría del creador del proyecto:

- **Contenido**: Notas, especificaciones, contexto adicional y documentación privada
- **Visibilidad**: Solo local, todo el contenido está en .gitignore
- **Uso por LLMs**: Pueden leer para contexto, pero NUNCA commitear o copiar datos sin autorización
- **Propiedad**: Contenido confidencial y propiedad intelectual del autor
- **Regla**: Preguntar antes de usar cualquier información de esta carpeta en código o documentación pública

### Nota para Desarrolladores
- **Humanos**: Tienen la última palabra sobre toda la documentación en `util/`
- **LLMs**: Deben pedir autorización antes de crear documentación técnica aquí
- **Estilo**: Documentación clara y profesional con uso mínimo de emojis

## Contexto Importante del Proyecto

### Propósito
Servicio FastAPI asíncrono que se autentica contra Taiga y permite gestionar proyectos, historias de usuario y tareas mediante una API REST completa.

Este servicio es parte del proyecto **VUCE-SIDOM DAI**, un sistema de digitalización de declaraciones aduaneras para Argentina. El servicio de Taiga se utiliza para gestionar las historias de usuario y tareas del desarrollo del módulo D4 (Operaciones IMEX).

**Funcionalidades principales:**
- Gestión completa de proyectos (listar, obtener detalles)
- CRUD de historias de usuario (crear, leer, actualizar, listar)
- CRUD de tareas (crear, leer, actualizar, eliminar, listar)
- Carga masiva de tareas desde archivos Markdown
- Consulta de metadatos (estados de tareas y historias)
- Endpoints de diagnóstico y troubleshooting

### Tecnologías Clave
- **Python 3.11+**: Lenguaje base con soporte para async/await
- **FastAPI**: Framework web asíncrono con documentación automática (OpenAPI/Swagger)
- **httpx**: Cliente HTTP asíncrono para integración con Taiga API
- **uv**: Gestor de dependencias moderno y rápido (reemplazo de pip/poetry)
- **Pydantic**: Validación y serialización de datos con type hints
- **pytest**: Framework de testing con fixtures y cobertura
- **pre-commit**: Hooks de Git para validación automática
- **black/isort/flake8/pylint**: Herramientas de formateo y linting

### Configuración Crítica
1. **Autenticación**:
   - Método recomendado: Token de API desde perfil de Taiga
   - Alternativo: Token de sesión del navegador (ver `taiga-devtools-example.md`)
   - Fallback: Usuario y contraseña (menos seguro)
2. **URL Base**: Debe terminar con `/` (ej: `https://taiga.example.com/api/v1/`)
3. **Puerto**: 8000 por defecto (configurable via UVICORN_PORT en .env)
4. **Diagnóstico**: Endpoints `/debug/*` para troubleshooting y validación
5. **Cache de Token**: TTL configurable (default 23h) con margen de renovación
6. **Validaciones**: Pre-commit hooks automáticos en cada commit

### Reglas de Desarrollo (Ver .llms)
- ❌ NO commitear datos del .env
- ❌ NO usar credenciales reales en ejemplos
- ❌ NO permitir commits que no pasen tests en main
- ✅ Usar pre-commit hooks para validación
- ✅ Mantener cobertura de tests
- ✅ Seguir estándares de código (flake8, pylint)

## Uso recomendado

### Para Humanos (Desarrolladores)
1. **Punto de entrada**: Leer `README.md` principal del proyecto
2. **Diagnóstico de tokens**: Seguir la guía (`taiga-devtools-example.md`) con la captura de ejemplo
3. **Desarrollo avanzado**: Consultar `DEVELOPMENT.md` para flujo completo
4. **Onboarding**: Este README como referencia rápida de estructura

### Para LLMs y Agentes
1. **Punto de entrada**: Leer `.llms` para reglas y contexto
2. **Documentación**: Crear archivos técnicos solo en `util/`
3. **Restricción**: NO modificar README.md (territorio humano)
4. **Actualizaciones**: Mantener sincronización con estructura del proyecto

### Contrato de Separación
- **Humanos** ↔ `README.md` (puntos de entrada, documentación de usuario)
- **LLMs** ↔ `util/` + `.llms` (documentación técnica, guías de desarrollo)
- **Respeto mutuo**: Cada parte mantiene su territorio

## Comandos Esenciales

```bash
# Instalación completa (recomendado)
./scripts/setup-dev.sh              # Instala todo: deps + hooks + validaciones

# Instalación manual
uv sync --dev                       # Solo dependencias
./scripts/setup-git-hooks.sh        # Solo hooks de Git

# Desarrollo local
uv run uvicorn app.main:app --reload  # Servidor con hot-reload
# Documentación interactiva: http://localhost:8000/docs

# Tests y validación
uv run pytest                       # Todos los tests
uv run pytest --cov=app             # Con cobertura
uv run pytest -m "not integration"  # Solo unitarios
uv run flake8 app/                  # Linting
uv run pylint app/                  # Análisis estático

# Pre-commit hooks
pre-commit run --all-files          # Ejecutar todas las validaciones
pre-commit install                  # Instalar hooks (si no usaste setup-dev.sh)

# Commits y versionado
./scripts/update.sh --local         # Commit local rápido
./scripts/update.sh --remote        # Análisis + commit + push
git commit -m "feat: mensaje"       # Git nativo (hooks automáticos)
SKIP_TESTS=1 git commit             # Omitir tests en desarrollo
```
