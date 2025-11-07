#!/bin/bash
# Script para analizar cambios y generar resumen para LLM

set -e

# Colores
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  ANÁLISIS DE CAMBIOS PARA RESUMEN FORMAL${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

# Obtener rama actual
BRANCH=$(git rev-parse --abbrev-ref HEAD)
REMOTE_BRANCH="origin/$BRANCH"

echo -e "${GREEN}📊 Información del contexto:${NC}"
echo "  Rama actual: $BRANCH"
echo "  Rama remota: $REMOTE_BRANCH"
echo ""

# Verificar si hay commits locales no pusheados
if ! git rev-parse "$REMOTE_BRANCH" &>/dev/null; then
    echo -e "${YELLOW}⚠️  Rama remota no existe, mostrando todos los cambios locales${NC}"
    COMMITS_AHEAD="all"
else
    COMMITS_AHEAD=$(git rev-list --count "$REMOTE_BRANCH..$BRANCH" 2>/dev/null || echo "0")
fi

echo -e "${GREEN}📝 Commits locales no pusheados: $COMMITS_AHEAD${NC}"
echo ""

# Mostrar diff de código
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  DIFF DE CÓDIGO (cambios no commiteados)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

if git diff --quiet && git diff --cached --quiet; then
    echo "No hay cambios sin commitear"
else
    git diff --stat
    echo ""
    echo "Archivos modificados:"
    git diff --name-only
    git diff --cached --name-only
fi

echo ""

# Mostrar commits locales
if [ "$COMMITS_AHEAD" != "0" ] && [ "$COMMITS_AHEAD" != "all" ]; then
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  COMMITS LOCALES (no pusheados)${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    git log "$REMOTE_BRANCH..$BRANCH" --oneline --decorate
    echo ""
fi

# Mostrar changelog temporal (sección Unreleased)
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  CHANGELOG TEMPORAL (Unreleased)${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""

if [ -f "CHANGELOG.md" ]; then
    # Extraer solo la sección Unreleased
    awk '/## \[Unreleased\]/,/## \[/' CHANGELOG.md | head -n -1
else
    echo "CHANGELOG.md no encontrado"
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  RESUMEN PARA LLM${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo ""
echo "Un LLM puede usar esta información para:"
echo "  1. Analizar el diff de código"
echo "  2. Revisar el changelog temporal"
echo "  3. Generar un resumen formal y profesional"
echo "  4. Crear un mensaje de commit descriptivo"
echo "  5. Actualizar el changelog con contexto completo"
echo ""
echo -e "${YELLOW}💡 Sugerencia:${NC}"
echo "   Copia esta salida y pide a un LLM que genere:"
echo "   - Mensaje de commit formal"
echo "   - Resumen para changelog"
echo "   - Descripción de cambios para el equipo"
echo ""
