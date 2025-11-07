# Guía de Desarrollo - Taiga FastAPI UV

## 🚀 Configuración Inicial

### Configuración Automática (Recomendado)

```bash
# Clonar el repositorio
git clone <repository-url>
cd taiga-fastapi-uv

# Configurar entorno completo
./scripts/setup-dev.sh
```

Este script instala:
- Dependencias de desarrollo con `uv`
- Hooks de Git (pre-commit, prepare-commit-msg, commit-msg, pre-push)
- Validaciones de código
- Sistema de changelog automático

### Configuración Manual

```bash
# 1. Instalar dependencias
uv sync --dev

# 2. Instalar todos los hooks de Git
uv run pre-commit install
uv run pre-commit install --hook-type prepare-commit-msg
uv run pre-commit install --hook-type commit-msg
uv run pre-commit install --hook-type pre-push
```

## 🔧 Herramientas Configuradas

### Pre-commit Hooks
- **Black**: Formateo de código (línea máx: 100)
- **isort**: Ordenamiento de imports
- **Flake8**: Linting básico
- **Pylint**: Análisis estático avanzado
- **MyPy**: Verificación de tipos
- **Pytest**: Ejecución de tests
- **Validación de secretos**: Previene commit de credenciales
- **Validación de datos**: Previene commit de datos personales

### GitLab CI/CD Pipeline
- **Validate**: Linting, formato, tipos
- **Test**: Tests unitarios e integración
- **Security**: Detección de secretos y vulnerabilidades
- **Deploy**: Despliegue automático (staging/production)

## 📋 Flujo de Trabajo Diario

### Desarrollo Normal

```bash
# 1. Iniciar servidor de desarrollo
uv run uvicorn app.main:app --reload

# 2. Hacer cambios en el código

# 3. Commit (todo automático)
git add .
git commit -m "feat(scope): descripción"

# Automáticamente se ejecuta:
# ✓ Formateo (black, isort)
# ✓ Linting (flake8, pylint)
# ✓ Validación de secretos
# ✓ Tests (si estás en main)
# ✓ Actualización de CHANGELOG.md
# ✓ Validación de formato de commit

# 4. Push
git push
```

### Comandos Opcionales (Makefile)

```bash
# Desarrollo
make dev                     # Servidor de desarrollo
make test                    # Ejecutar tests
make lint                    # Linting completo
make format                  # Formatear código

# Validación
make ci                      # Simular pipeline de CI

# Changelog
make changelog               # Ver changelog completo
make changelog-unreleased    # Ver cambios pendientes

# Utilidades
make clean                   # Limpiar archivos temporales
make help                    # Ver todos los comandos
```

## 🛡️ Reglas de Seguridad

### ❌ Prohibido Absolutamente
- Commitear archivos `.env` con datos reales
- Usar credenciales reales en ejemplos o tests
- Hacer commits a `main` que no pasen tests
- Loggear credenciales (excepto en Docker con env vars)
- Incluir datos personales en el código

### ✅ Obligatorio
- Todos los commits deben pasar pre-commit hooks
- Tests unitarios para nuevo código
- Cobertura de tests > 80% para `main`
- Usar datos genéricos en ejemplos
- Leer `.llms` antes de contribuir

### 🔄 Flexibilidad en Desarrollo
- **Ramas feature/develop**: Puedes omitir tests con `SKIP_TESTS=1`
- **Rama main**: Tests siempre obligatorios
- **Work-in-progress**: Usa `make commit-wip` para commits temporales

## 🧪 Testing

### Estructura de Tests
```
tests/
├── __init__.py
├── conftest.py              # Configuración compartida
├── test_main.py             # Tests de FastAPI
└── test_taiga_client.py     # Tests del cliente Taiga
```

### Tipos de Tests
```bash
make test                    # Todos los tests
make test-unit              # Solo unitarios
make test-integration       # Solo integración
make test-watch             # Modo watch
```

### Marcadores de Tests
- `@pytest.mark.integration`: Tests que requieren servicios externos
- Sin marcador: Tests unitarios rápidos

## 🔍 Debugging

### Endpoints de Diagnóstico
- `POST /debug/auth`: Verificar autenticación
- `GET /debug/state`: Estado del cliente
- `GET /debug/connection`: Test de conexión
- `POST /debug/cache/clear`: Limpiar cache de token

### Logs y Debugging
```bash
# Ejecutar con logs detallados
uv run uvicorn app.main:app --reload --log-level debug

# Tests con output detallado
make test -- -v -s

# Debugging de pre-commit
uv run pre-commit run --all-files --verbose
```

## 📁 Estructura del Proyecto

```
taiga-fastapi-uv/
├── .llms                    # Contexto para modelos IA
├── .pre-commit-config.yaml  # Configuración pre-commit
├── .gitlab-ci.yml          # Pipeline CI/CD
├── Makefile                # Comandos de desarrollo
├── DEVELOPMENT.md          # Esta guía
├── app/                    # Código fuente
├── tests/                  # Tests
├── util/                   # Documentación y recursos
├── scripts/                # Scripts de utilidad
└── pyproject.toml          # Configuración del proyecto
```

## 🚦 Flujo de Trabajo Git

### Desarrollo Local
1. Crear rama feature: `git checkout -b feature/nueva-funcionalidad`
2. Desarrollar y hacer commits:
   ```bash
   git add .
   git commit -m "feat(scope): descripción"
   # Todo se valida automáticamente
   ```
3. Formato de commits (Conventional Commits):
   - `feat(scope): descripción` - Nueva funcionalidad
   - `fix(scope): descripción` - Corrección de errores
   - `docs: descripción` - Cambios en documentación
   - Ver `util/commit-guidelines.md` para más detalles
4. Changelog se actualiza automáticamente en cada commit
5. Push y crear Merge Request:
   ```bash
   git push origin feature/nueva-funcionalidad
   ```

### Pipeline CI/CD
1. **Validate**: Formato, linting, tipos
2. **Test**: Tests unitarios e integración
3. **Security**: Detección de secretos
4. **Deploy**: Automático a staging, manual a production

### Protección de `main`
- Solo commits que pasen **todos** los tests
- Quality gate con cobertura mínima 80%
- Revisión obligatoria de código
- Pipeline completo debe ser verde

## 📝 Sistema de Commits y Changelog

### Formato de Commits (Conventional Commits)

Todos los commits deben seguir el formato:
```
tipo(ámbito): descripción
```

**Tipos válidos:**
- `feat`: Nueva funcionalidad
- `fix`: Corrección de errores
- `docs`: Cambios en documentación
- `refactor`: Refactorización
- `test`: Tests
- `chore`: Mantenimiento

**Ejemplos:**
```bash
feat(auth): agregar soporte para tokens de sesión
fix(client): corregir timeout de conexión
docs: actualizar guía de instalación
test(api): agregar tests para endpoints de debug
```

### Changelog Automático

El CHANGELOG.md se actualiza automáticamente:
- En cada commit válido
- Según el tipo de commit
- Mantiene formato Keep a Changelog
- Agrupa cambios por categoría

**Ver changelog:**
```bash
make changelog              # Ver changelog completo
make changelog-unreleased   # Ver cambios no liberados
```

### Validación Automática

Los hooks de Git validan:
- Formato de commit (commit-msg)
- Tests antes de push a main (pre-push)
- Actualización de changelog (pre-commit)

Ver guía completa en `util/commit-guidelines.md`

## 🆘 Solución de Problemas

### Pre-commit Falla
```bash
# Ver detalles del error
uv run pre-commit run --all-files --verbose

# Arreglar formato automáticamente
make format

# Ejecutar solo un hook específico
uv run pre-commit run black --all-files
```

### Tests Fallan
```bash
# Ejecutar con más detalle
make test -- -v -s --tb=long

# Ejecutar solo un test específico
uv run pytest tests/test_main.py::test_specific -v

# Ver cobertura detallada
make test -- --cov-report=html
```

### CI Pipeline Falla
1. Revisar logs en GitLab CI
2. Reproducir localmente: `make ci`
3. Arreglar problemas específicos
4. Verificar con `make pre-commit`

## 📚 Recursos Adicionales

- **README.md**: Documentación principal del usuario
- **util/README.md**: Estructura del proyecto y contexto
- **.llms**: Reglas imperantes para modelos IA
- **FastAPI Docs**: `http://localhost:8000/docs` (servidor activo)
- **Coverage Report**: `htmlcov/index.html` (después de tests)

---

**⚠️ IMPORTANTE**: Este proyecto tiene reglas estrictas de calidad y seguridad. Lee el archivo `.llms` antes de contribuir.
