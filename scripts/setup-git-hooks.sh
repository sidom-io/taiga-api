#!/bin/bash
# Script para verificar que pre-commit esté instalado correctamente

set -e

echo "🔧 Verificando instalación de hooks..."

if [ ! -d ".git/hooks" ]; then
    echo "❌ Directorio .git/hooks no existe"
    echo "¿Estás en la raíz del repositorio?"
    exit 1
fi

# Verificar que pre-commit esté instalado
if ! command -v pre-commit &> /dev/null; then
    echo "❌ pre-commit no está instalado"
    echo "Ejecuta: uv sync --dev"
    exit 1
fi

# Instalar todos los hooks de pre-commit
echo "📦 Instalando hooks de pre-commit..."
pre-commit install
pre-commit install --hook-type prepare-commit-msg
pre-commit install --hook-type commit-msg  
pre-commit install --hook-type pre-push

echo ""
echo "✅ Sistema de hooks configurado correctamente"
echo ""
echo "Flujo de trabajo:"
echo "  1. git add ."
echo "  2. git commit -m \"tipo: descripción\""
echo "  3. Automáticamente se ejecutan:"
echo "     - Formateo (black, isort)"
echo "     - Linting (flake8, pylint)"
echo "     - Tests (si estás en main)"
echo "     - Validación de formato"
echo "     - Actualización de CHANGELOG.md"
echo ""
echo "💡 Todo funciona con comandos git nativos"