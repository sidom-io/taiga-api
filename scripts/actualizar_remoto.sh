#!/bin/bash
# Script para ejecutar flujo completo de commit y push usando uv

set -e

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🚀 Flujo de actualización remota"
echo "================================"
echo ""

# Verificar que uv esté instalado
if ! command -v uv &> /dev/null; then
    echo -e "${RED}❌ uv no está instalado${NC}"
    echo "Instala uv desde: https://github.com/astral-sh/uv"
    exit 1
fi

# Verificar que estamos en un repositorio git
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}❌ No estás en un repositorio git${NC}"
    exit 1
fi

# Verificar si hay cambios para commitear
if git diff --quiet && git diff --cached --quiet; then
    echo -e "${YELLOW}⚠️  No hay cambios para commitear${NC}"
    exit 0
fi

# Mostrar estado actual
echo "📋 Estado actual:"
git status --short
echo ""

# Agregar todos los cambios
echo "📦 Agregando cambios..."
git add .
echo ""

# Solicitar mensaje de commit si no se proporciona
if [ -z "$1" ]; then
    echo "💬 Ingresa el mensaje de commit (formato: tipo(ámbito): descripción)"
    echo "   Ejemplos:"
    echo "   - feat(auth): agregar nueva funcionalidad"
    echo "   - fix(client): corregir error de conexión"
    echo "   - docs: actualizar README"
    echo ""
    read -p "Mensaje: " COMMIT_MSG
else
    COMMIT_MSG="$1"
fi

# Validar formato básico
if ! echo "$COMMIT_MSG" | grep -qE "^(feat|fix|docs|style|refactor|test|chore|perf|ci|build)(\(.+\))?: .+"; then
    echo -e "${RED}❌ Formato de commit inválido${NC}"
    echo "Formato requerido: tipo(ámbito): descripción"
    echo "Tipos válidos: feat, fix, docs, style, refactor, test, chore, perf, ci, build"
    exit 1
fi

echo ""
echo "🔍 Ejecutando validaciones pre-commit..."
echo ""

# Ejecutar pre-commit hooks
if ! uv run pre-commit run --all-files; then
    echo -e "${RED}❌ Validaciones pre-commit fallaron${NC}"
    echo "Revisa los errores arriba y corrige los problemas"
    exit 1
fi

echo ""
echo "✅ Validaciones pasaron"
echo ""

# Hacer commit
echo "💾 Creando commit..."
if ! git commit -m "$COMMIT_MSG"; then
    echo -e "${RED}❌ Commit falló${NC}"
    exit 1
fi

echo ""
echo "✅ Commit creado exitosamente"
echo ""

# Obtener rama actual
BRANCH=$(git rev-parse --abbrev-ref HEAD)

# Preguntar si hacer push
read -p "🚀 ¿Hacer push a origin/$BRANCH? (s/N): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Ss]$ ]]; then
    echo "📤 Haciendo push..."
    if git push origin "$BRANCH"; then
        echo ""
        echo -e "${GREEN}✅ Push exitoso a origin/$BRANCH${NC}"
    else
        echo ""
        echo -e "${RED}❌ Push falló${NC}"
        exit 1
    fi
else
    echo "⏭️  Push omitido"
fi

echo ""
echo -e "${GREEN}🎉 ¡Proceso completado!${NC}"
echo ""
echo "📋 Resumen:"
echo "  - Commit: $COMMIT_MSG"
echo "  - Rama: $BRANCH"
echo "  - CHANGELOG.md actualizado automáticamente"
