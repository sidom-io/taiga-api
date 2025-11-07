#!/bin/bash
# Script para actualizar CHANGELOG.md automáticamente

COMMIT_MSG_FILE=$1
COMMIT_SOURCE=$2

# Solo procesar commits normales (no merges, ammends, etc)
if [ -n "$COMMIT_SOURCE" ]; then
  exit 0
fi

# Leer mensaje del commit
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

# Validar formato Conventional Commits
if ! echo "$COMMIT_MSG" | grep -qE "^(feat|fix|docs|style|refactor|test|chore|perf|ci|build)(\(.+\))?: .+"; then
  echo "⚠️  Commit no sigue formato convencional, saltando changelog"
  exit 0
fi

# Extraer tipo y descripción
TYPE=$(echo "$COMMIT_MSG" | sed -E "s/^([a-z]+)(\(.+\))?: .*/\1/")
DESC=$(echo "$COMMIT_MSG" | sed -E "s/^[a-z]+(\(.+\))?: (.+)/\2/")

# Determinar sección
case "$TYPE" in
  feat) SECTION="Added" ;;
  fix) SECTION="Fixed" ;;
  *) SECTION="Changed" ;;
esac

# Actualizar CHANGELOG.md
if [ -f "CHANGELOG.md" ]; then
  # Crear entrada
  ENTRY="- $DESC"

  # Buscar sección Unreleased y agregar entrada
  if grep -q "## \[Unreleased\]" CHANGELOG.md; then
    # Verificar si la sección existe
    if grep -A 20 "## \[Unreleased\]" CHANGELOG.md | grep -q "### $SECTION"; then
      # Agregar a sección existente (después del título de la sección)
      awk -v section="### $SECTION" -v entry="$ENTRY" '
        $0 ~ section {print; print entry; next}
        {print}
      ' CHANGELOG.md > CHANGELOG.md.tmp && mv CHANGELOG.md.tmp CHANGELOG.md
    else
      # Crear nueva sección después de Unreleased
      awk -v section="$SECTION" -v entry="$ENTRY" '
        /## \[Unreleased\]/ {print; print ""; print "### " section; print entry; next}
        {print}
      ' CHANGELOG.md > CHANGELOG.md.tmp && mv CHANGELOG.md.tmp CHANGELOG.md
    fi

    git add CHANGELOG.md
    echo "✅ CHANGELOG.md actualizado: $ENTRY"
  fi
fi
