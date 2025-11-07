#!/bin/bash
# Script principal para actualizar código local o remoto

set -e

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Función de ayuda
show_help() {
    echo "Uso: $0 [--local|--remote] [mensaje]"
    echo ""
    echo "Opciones:"
    echo "  --local   Commit local rápido (desarrollo)"
    echo "  --remote  Análisis completo + commit formal + push"
    echo ""
    echo "Ejemplos:"
    echo "  $0 --local \"feat: cambio rápido\""
    echo "  $0 --remote"
    echo ""
}

# Verificar argumentos
if [ $# -eq 0 ]; then
    show_help
    exit 1
fi

MODE=$1
shift

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

# ============================================================================
# MODO LOCAL: Commit rápido para desarrollo
# ============================================================================
if [ "$MODE" = "--local" ]; then
    echo -e "${GREEN}🚀 Modo LOCAL: Commit rápido${NC}"
    echo ""

    # Verificar si hay cambios
    if git diff --quiet && git diff --cached --quiet; then
        echo -e "${YELLOW}⚠️  No hay cambios para commitear${NC}"
        exit 0
    fi

    # Mostrar estado
    echo "📋 Cambios:"
    git status --short
    echo ""

    # Obtener mensaje de commit
    if [ -z "$1" ]; then
        echo "💬 Ingresa el mensaje de commit:"
        read -p "Mensaje: " COMMIT_MSG
    else
        COMMIT_MSG="$1"
    fi

    # Validar formato básico
    if ! echo "$COMMIT_MSG" | grep -qE "^(feat|fix|docs|style|refactor|test|chore|perf|ci|build)(\(.+\))?: .+"; then
        echo -e "${RED}❌ Formato inválido${NC}"
        echo "Formato: tipo(ámbito): descripción"
        exit 1
    fi

    # Agregar y commitear
    git add .

    echo ""
    echo "🔍 Ejecutando validaciones..."
    if ! uv run pre-commit run --all-files; then
        echo -e "${RED}❌ Validaciones fallaron${NC}"
        exit 1
    fi

    echo ""
    git commit -m "$COMMIT_MSG"

    echo ""
    echo -e "${GREEN}✅ Commit local creado${NC}"
    echo "💡 Usa '$0 --remote' cuando estés listo para push"

# ============================================================================
# MODO REMOTE: Análisis completo + commit formal + push
# ============================================================================
elif [ "$MODE" = "--remote" ]; then
    echo -e "${BLUE}🌐 Modo REMOTE: Análisis y push${NC}"
    echo ""

    # Paso 1: Mostrar análisis de cambios
    echo -e "${YELLOW}📊 Analizando cambios...${NC}"
    echo ""

    if [ -f "./scripts/analyze-changes.sh" ]; then
        ./scripts/analyze-changes.sh
    else
        echo -e "${RED}❌ Script analyze-changes.sh no encontrado${NC}"
        exit 1
    fi

    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  CONFIRMACIÓN${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Has revisado el análisis de cambios arriba."
    echo ""
    echo "Opciones:"
    echo "  1. Continuar con commit y push"
    echo "  2. Generar resumen con LLM (recomendado)"
    echo "  3. Cancelar"
    echo ""
    read -p "Selecciona (1/2/3): " CHOICE

    case $CHOICE in
        1)
            # Commit directo
            echo ""
            echo "💬 Ingresa el mensaje de commit formal:"
            read -p "Mensaje: " COMMIT_MSG

            if [ -z "$COMMIT_MSG" ]; then
                echo -e "${RED}❌ Mensaje vacío${NC}"
                exit 1
            fi

            # Validar formato
            if ! echo "$COMMIT_MSG" | grep -qE "^(feat|fix|docs|style|refactor|test|chore|perf|ci|build)(\(.+\))?: .+"; then
                echo -e "${RED}❌ Formato inválido${NC}"
                exit 1
            fi
            ;;
        2)
            # Modo LLM
            echo ""
            echo -e "${YELLOW}🤖 Modo LLM activado${NC}"
            echo ""
            echo "Instrucciones:"
            echo "  1. Copia el análisis de cambios mostrado arriba"
            echo "  2. Pide a un LLM que genere:"
            echo "     - Mensaje de commit formal"
            echo "     - Resumen para changelog"
            echo "  3. Vuelve aquí y pega el mensaje generado"
            echo ""
            read -p "Presiona Enter cuando tengas el mensaje del LLM..."
            echo ""
            echo "💬 Pega el mensaje de commit generado por el LLM:"
            read -p "Mensaje: " COMMIT_MSG

            if [ -z "$COMMIT_MSG" ]; then
                echo -e "${RED}❌ Mensaje vacío${NC}"
                exit 1
            fi
            ;;
        3)
            echo "❌ Cancelado"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Opción inválida${NC}"
            exit 1
            ;;
    esac

    # Verificar si hay cambios sin commitear
    if ! git diff --quiet || ! git diff --cached --quiet; then
        echo ""
        echo "📦 Agregando cambios..."
        git add .

        echo "🔍 Ejecutando validaciones..."
        if ! uv run pre-commit run --all-files; then
            echo -e "${RED}❌ Validaciones fallaron${NC}"
            exit 1
        fi

        echo ""
        git commit -m "$COMMIT_MSG"
    fi

    # Push
    BRANCH=$(git rev-parse --abbrev-ref HEAD)
    echo ""
    echo "🚀 Haciendo push a origin/$BRANCH..."

    if git push origin "$BRANCH"; then
        echo ""
        echo -e "${GREEN}✅ Push exitoso${NC}"
        echo ""
        echo "📋 Resumen:"
        echo "  - Commit: $COMMIT_MSG"
        echo "  - Rama: $BRANCH"
        echo "  - CHANGELOG.md actualizado"
    else
        echo -e "${RED}❌ Push falló${NC}"
        exit 1
    fi

else
    echo -e "${RED}❌ Modo inválido: $MODE${NC}"
    show_help
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 ¡Completado!${NC}"
