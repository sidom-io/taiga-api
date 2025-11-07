# Flujo de Trabajo con LLM

## Propósito

El modo `--remote` del script `update.sh` está diseñado para trabajar con LLMs (Large Language Models) y generar resúmenes profesionales de cambios antes de hacer push.

## Problema que Resuelve

Durante el desarrollo:
- Haces múltiples commits locales rápidos
- El changelog temporal se llena de entradas técnicas
- El diff de código puede ser extenso
- Necesitas un resumen formal para el equipo

## Solución

El script analiza:
1. **Diff de código**: Qué archivos cambiaron y cómo
2. **Changelog temporal**: Entradas de commits locales
3. **Commits locales**: Historial no pusheado

Y permite que un LLM genere:
- Mensaje de commit formal y descriptivo
- Resumen profesional para changelog
- Contexto completo para el equipo

## Flujo de Uso

### 1. Desarrollo Normal

```bash
# Durante desarrollo: commits locales rápidos
./scripts/update.sh --local "feat: agregar validación"
./scripts/update.sh --local "fix: corregir error"
./scripts/update.sh --local "refactor: mejorar código"
```

### 2. Antes de Push

```bash
# Ejecutar análisis
./scripts/update.sh --remote
```

### 3. El Script Muestra

```
═══════════════════════════════════════════════════════════
  DIFF DE CÓDIGO (cambios no commiteados)
═══════════════════════════════════════════════════════════

app/auth.py | 45 ++++++++++++++++++++++++++++++++++++++++++
tests/test_auth.py | 23 ++++++++++++++++++++
2 files changed, 68 insertions(+)

═══════════════════════════════════════════════════════════
  COMMITS LOCALES (no pusheados)
═══════════════════════════════════════════════════════════

abc123 feat: agregar validación
def456 fix: corregir error
ghi789 refactor: mejorar código

═══════════════════════════════════════════════════════════
  CHANGELOG TEMPORAL (Unreleased)
═══════════════════════════════════════════════════════════

### Added
- agregar validación
- mejorar código

### Fixed
- corregir error
```

### 4. Opciones

**Opción 1: Commit directo**
- Escribes el mensaje manualmente
- Útil si los cambios son simples

**Opción 2: Generar con LLM** (Recomendado)
- Copias el análisis completo
- Se lo pasas a un LLM (ChatGPT, Claude, etc.)
- El LLM genera un resumen profesional
- Pegas el mensaje generado

## Ejemplo de Prompt para LLM

```
Analiza estos cambios y genera un mensaje de commit formal:

[Pegar análisis del script]

Por favor genera:
1. Un mensaje de commit en formato Conventional Commits
2. Que sea descriptivo y profesional
3. Que explique el contexto completo de los cambios
4. Que sea entendible para el equipo
```

## Ejemplo de Respuesta del LLM

```
feat(auth): implementar sistema de validación de tokens con tests

Implementado sistema completo de validación de tokens de autenticación
incluyendo:
- Validación de formato y expiración de tokens
- Manejo de errores con mensajes descriptivos
- Tests unitarios con cobertura completa
- Refactorización de código para mejor mantenibilidad

Los cambios mejoran la seguridad y robustez del sistema de autenticación.
```

## Beneficios

- **Commits profesionales**: Mensajes claros y descriptivos
- **Contexto completo**: El LLM ve todo el panorama
- **Ahorro de tiempo**: No escribir resúmenes manualmente
- **Mejor comunicación**: El equipo entiende los cambios
- **Changelog útil**: Entradas formales y profesionales

## Comandos Relacionados

```bash
# Solo ver análisis (sin commit)
./scripts/analyze-changes.sh

# Commit local rápido
./scripts/update.sh --local "mensaje"

# Análisis + commit + push
./scripts/update.sh --remote
```

## Integración con .llms

Este flujo respeta el contrato LLM-Humano:
- LLMs ayudan a generar resúmenes profesionales
- Humanos tienen la última palabra
- Documentación técnica en util/
- Proceso transparente y controlado
