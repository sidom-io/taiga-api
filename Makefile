# Makefile para Taiga FastAPI UV
# Comandos comunes para desarrollo

.PHONY: help install dev test lint format clean pre-commit ci

# Configuración
PYTHON := uv run python
PYTEST := uv run pytest
FLAKE8 := uv run flake8
BLACK := uv run black
ISORT := uv run isort
PYLINT := uv run pylint
PRECOMMIT := uv run pre-commit

help: ## Mostrar esta ayuda
	@echo "Comandos disponibles:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## Instalar dependencias
	@echo "📦 Instalando dependencias..."
	uv sync --dev

setup-dev: ## Configurar entorno de desarrollo completo
	@echo "🚀 Configurando entorno de desarrollo..."
	./scripts/setup-dev.sh

dev: ## Iniciar servidor de desarrollo
	@echo "🚀 Iniciando servidor de desarrollo..."
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test: ## Ejecutar todos los tests
	@echo "🧪 Ejecutando tests..."
	$(PYTEST) tests/ -v --cov=app --cov-report=term-missing

test-unit: ## Ejecutar solo tests unitarios
	@echo "🧪 Ejecutando tests unitarios..."
	$(PYTEST) tests/ -v -m "not integration"

test-integration: ## Ejecutar solo tests de integración
	@echo "🔗 Ejecutando tests de integración..."
	$(PYTEST) tests/ -v -m integration

test-watch: ## Ejecutar tests en modo watch
	@echo "👀 Ejecutando tests en modo watch..."
	$(PYTEST) tests/ -v --cov=app -f

lint: ## Ejecutar linting (flake8 + pylint)
	@echo "🔍 Ejecutando linting..."
	$(FLAKE8) app/ --max-line-length=100 --extend-ignore=E203,W503
	$(PYLINT) app/ --rcfile=pyproject.toml

format: ## Formatear código (black + isort)
	@echo "🎨 Formateando código..."
	$(BLACK) app/ tests/
	$(ISORT) app/ tests/

format-check: ## Verificar formato sin modificar
	@echo "🎨 Verificando formato..."
	$(BLACK) --check --diff app/ tests/
	$(ISORT) --check-only --diff app/ tests/

type-check: ## Verificar tipos con mypy
	@echo "🔍 Verificando tipos..."
	uv run mypy app/ --config-file=pyproject.toml

pre-commit: ## Ejecutar pre-commit en todos los archivos
	@echo "🔧 Ejecutando pre-commit..."
	$(PRECOMMIT) run --all-files

pre-commit-skip-tests: ## Ejecutar pre-commit omitiendo tests
	@echo "🔧 Ejecutando pre-commit (sin tests)..."
	SKIP_TESTS=1 $(PRECOMMIT) run --all-files

pre-commit-install: ## Instalar hooks de pre-commit
	@echo "🔧 Instalando pre-commit hooks..."
	$(PRECOMMIT) install

ci: ## Ejecutar todas las validaciones como en CI
	@echo "🚀 Ejecutando validaciones de CI..."
	@echo "1. Formato..."
	@$(MAKE) format-check
	@echo "2. Linting..."
	@$(MAKE) lint
	@echo "3. Type checking..."
	@$(MAKE) type-check
	@echo "4. Tests..."
	@$(MAKE) test
	@echo "✅ Todas las validaciones pasaron!"

clean: ## Limpiar archivos temporales
	@echo "🧹 Limpiando archivos temporales..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .coverage htmlcov/ .pytest_cache/ .mypy_cache/

docs: ## Generar documentación
	@echo "📚 Generando documentación..."
	@echo "Documentación disponible en:"
	@echo "  - README.md (principal - punto de entrada humano)"
	@echo "  - .llms (punto de entrada para LLMs)"
	@echo "  - util/README.md (estructura del proyecto)"
	@echo "  - util/DEVELOPMENT.md (guía de desarrollo detallada)"
	@echo "  - http://localhost:8000/docs (FastAPI docs - requiere servidor activo)"

security: ## Ejecutar verificaciones de seguridad
	@echo "🔒 Ejecutando verificaciones de seguridad..."
	@echo "Verificando secretos..."
	@$(PYTHON) -c "
import re
import sys
import os

patterns = [
    r'TAIGA_PASSWORD=(?!.*example|.*placeholder|.*your_password)',
    r'TAIGA_USERNAME=(?!.*example|.*placeholder|.*your_username)',
    r'TAIGA_AUTH_TOKEN=(?!.*example|.*placeholder|.*your_token|.*eyJ0eXAi)',
]

violations = []
for root, dirs, files in os.walk('.'):
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    for file in files:
        if file.endswith(('.py', '.md', '.yml', '.yaml')):
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r') as f:
                    content = f.read()
                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            violations.append(f'{filepath}: {pattern}')
            except:
                pass

if violations:
    print('❌ VIOLACIONES DE SEGURIDAD:')
    for v in violations:
        print(f'  {v}')
    sys.exit(1)
else:
    print('✅ No se detectaron violaciones de seguridad')
"

# Comandos de commit convenientes
commit-wip: ## Commit work-in-progress (omite tests)
	@echo "💾 Commit work-in-progress..."
	@echo "⚠️  Este commit omite tests - úsalo solo en ramas de desarrollo"
	@SKIP_TESTS=1 git add . && git commit -m "WIP: $(shell read -p 'Mensaje del commit: ' msg && echo $$msg)"

commit-safe: ## Commit con todas las validaciones
	@echo "💾 Commit con validaciones completas..."
	@git add . && git commit -m "$(shell read -p 'Mensaje del commit: ' msg && echo $$msg)"

changelog: ## Ver changelog actual
	@echo "📋 Changelog actual:"
	@head -50 CHANGELOG.md

changelog-unreleased: ## Ver cambios no liberados
	@echo "📋 Cambios no liberados:"
	@sed -n '/## \[Unreleased\]/,/## \[/p' CHANGELOG.md | head -n -1

# Comandos de desarrollo rápido
quick-test: ## Test rápido (sin cobertura)
	$(PYTEST) tests/ -x -v

quick-lint: ## Linting rápido (solo flake8)
	$(FLAKE8) app/ --max-line-length=100 --extend-ignore=E203,W503

# Información del proyecto
info: ## Mostrar información del proyecto
	@echo "📋 Información del Proyecto"
	@echo "=========================="
	@echo "Nombre: Taiga FastAPI UV"
	@echo "Descripción: Servicio FastAPI para integración con Taiga"
	@echo "Python: $(shell python --version 2>/dev/null || echo 'No disponible')"
	@echo "UV: $(shell uv --version 2>/dev/null || echo 'No instalado')"
	@echo ""
	@echo "📁 Estructura:"
	@echo "  app/           - Código fuente"
	@echo "  tests/         - Tests"
	@echo "  util/          - Documentación y recursos"
	@echo "  scripts/       - Scripts de utilidad"
	@echo ""
	@echo "🔧 Sistema Integrado:"
	@echo "  - Pre-commit hooks con validación completa"
	@echo "  - Git hooks (commit-msg, pre-push)"
	@echo "  - Changelog automático (Conventional Commits)"
	@echo "  - GitLab CI/CD con quality gate"
	@echo "  - Tests con cobertura mínima 80%"
	@echo "  - Linting (Flake8 + Pylint)"
	@echo "  - Formateo (Black + isort)"
	@echo "  - Type checking (MyPy)"
	@echo ""
	@echo "📖 Documentación:"
	@echo "  - README.md (punto de entrada)"
	@echo "  - util/system-overview.md (visión general)"
	@echo "  - util/DEVELOPMENT.md (guía desarrollo)"
	@echo "  - util/commit-guidelines.md (formato commits)"