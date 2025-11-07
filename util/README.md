# Punto de entrada

Esta carpeta almacena documentación y material de apoyo para diagnosticar la integración con el proyecto. Además, sirve como mapa rápido de la estructura del repositorio y contexto importante para modelos de IA y desarrolladores.

## Árbol del proyecto

```text
taiga-fastapi-uv/
├── .llms                      # Punto de entrada para LLMs (contrato)
├── .pre-commit-config.yaml    # Configuración pre-commit hooks
├── .gitlab-ci.yml            # Pipeline CI/CD GitLab
├── Makefile                  # Comandos de desarrollo
├── app/
│   ├── __init__.py            # Marca el paquete y expone la app
│   ├── main.py                # Entrypoint de FastAPI y rutas públicas/debug
│   ├── schemas.py             # Modelos Pydantic usados por las rutas
│   └── taiga_client.py        # Cliente httpx con cache de token y utilidades
├── tests/                     # Tests del proyecto
├── scripts/                   # Scripts de utilidad
├── pyproject.toml             # Configuración del proyecto y dependencias
├── README.md                  # Guía principal (punto de entrada humano)
├── uv.lock                    # Resolución exacta de dependencias (uv)
└── util/                      # Documentación técnica (territorio LLM)
    ├── README.md              # Este archivo (mantenido por humanos)
    ├── DEVELOPMENT.md         # Guía completa de desarrollo (creada por LLM)
    ├── taiga-devtools-example.md  # Procedimiento para extraer tokens (LLM)
    └── taiga_token_example.jpg    # Captura con headers de autorización
```

## Archivos en esta carpeta

**`README.md`** - Este archivo (mantenido por humanos)
**`system-overview.md`** - Visión general del sistema integrado
**`vuce-sidom-architecture.md`** - Arquitectura completa del proyecto VUCE-SIDOM DAI
**`kit-maria-integration.md`** - Integración con KIT Malvina/Maria (bloqueante crítico)
**`DEVELOPMENT.md`** - Guía completa de desarrollo
**`commit-guidelines.md`** - Guías de commits y versionado
**`llm-workflow.md`** - Flujo de trabajo con LLM para commits profesionales
**`troubleshooting-uv-python.md`** - Resolución de errores comunes con uv y Python 3.13
**`taiga-devtools-example.md`** - Cómo extraer tokens del navegador
**`taiga_token_example.jpg`** - Captura de pantalla con headers de autorización
**`llm-docs-proyect/`** - Documentación privada del proyecto (contenido en .gitignore)

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
Servicio FastAPI asíncrono que se autentica contra Taiga y permite crear tareas mediante un endpoint REST.

Este servicio es parte del proyecto **VUCE-SIDOM DAI**, un sistema de digitalización de declaraciones aduaneras para Argentina. El servicio de Taiga se utiliza para gestionar las historias de usuario y tareas del desarrollo del módulo D4 (Operaciones IMEX).

### Tecnologías Clave
- **Python 3.11+**: Lenguaje base con soporte para async/await
- **FastAPI**: Framework web asíncrono con documentación automática
- **httpx**: Cliente HTTP asíncrono para integración con Taiga API
- **uv**: Gestor de dependencias moderno y rápido
- **Pydantic**: Validación y serialización de datos

### Configuración Crítica
1. **Autenticación**: Token de sesión del navegador (método recomendado)
2. **URL Base**: Debe terminar con `/` (ej: `https://taiga.example.com/api/v1/`)
3. **Puerto**: 8000 por defecto (configurable via UVICORN_PORT)
4. **Diagnóstico**: Endpoints `/debug/*` para troubleshooting

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
# Instalación inicial
uv sync

# Desarrollo local
uv run uvicorn app.main:app --reload

# Tests y validación
uv run pytest
uv run flake8 app/
uv run pylint app/

# Pre-commit (después de instalación)
pre-commit run --all-files
```
