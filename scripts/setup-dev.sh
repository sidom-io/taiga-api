#!/bin/bash
# Script de configuración para desarrollo

set -e  # Salir si hay errores

echo "🚀 Configurando entorno de desarrollo para Taiga FastAPI UV..."

# Verificar que uv está instalado
if ! command -v uv &> /dev/null; then
    echo "❌ uv no está instalado. Instálalo desde: https://github.com/astral-sh/uv"
    exit 1
fi

echo "📦 Instalando dependencias..."
uv sync --dev

echo "🔧 Instalando pre-commit hooks..."
uv run pre-commit install
uv run pre-commit install --hook-type prepare-commit-msg
uv run pre-commit install --hook-type commit-msg
uv run pre-commit install --hook-type pre-push

echo "✅ Hooks instalados - git commit ejecutará todas las validaciones automáticamente"

echo "🧪 Ejecutando validaciones iniciales..."
echo "  - Formateando código..."
uv run black app/ tests/
uv run isort app/ tests/

echo "  - Ejecutando linting..."
uv run flake8 app/ --max-line-length=100 --extend-ignore=E203,W503

echo "  - Ejecutando tests..."
uv run pytest tests/ -v

echo "  - Ejecutando pre-commit en todos los archivos..."
uv run pre-commit run --all-files

echo ""
echo "✅ ¡Configuración completada!"
echo ""
echo "📋 Comandos útiles:"
echo "  uv run uvicorn app.main:app --reload    # Iniciar servidor de desarrollo"
echo "  uv run pytest                          # Ejecutar tests"
echo "  uv run pre-commit run --all-files      # Ejecutar todas las validaciones"
echo "  uv run flake8 app/                     # Linting"
echo "  uv run black app/ tests/               # Formatear código"
echo ""
echo "📖 Documentación disponible en:"
echo "  - README.md (principal)"
echo "  - util/README.md (estructura del proyecto)"
echo "  - .llms (reglas para modelos de IA)"
echo ""
echo "⚠️  IMPORTANTE: Lee el archivo .llms para entender las reglas del proyecto"