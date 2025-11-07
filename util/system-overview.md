# Visión General del Sistema

## Arquitectura de Documentación y Validación

Este proyecto implementa un sistema coherente e integrado de documentación, testing y validación que garantiza calidad y consistencia.

## Componentes del Sistema

### 1. Sistema de Documentación

**Estructura:**
```
├── README.md                    # Punto de entrada humano
├── .llms                        # Punto de entrada para LLMs
├── CHANGELOG.md                 # Registro automático de cambios
└── util/                        # Documentación técnica
    ├── README.md                # Índice de documentación
    ├── DEVELOPMENT.md           # Guía de desarrollo
    └── commit-guidelines.md     # Guías de commits
```

**Contrato LLM-Humano:**
- LLMs crean documentación en `util/` con autorización previa
- Humanos mantienen README.md y tienen autoridad final
- Estilo profesional con emojis mínimos (solo para seguridad)

### 2. Sistema de Validación

**Pre-commit Hooks:**
- Formato de código (Black, isort)
- Linting (Flake8, Pylint)
- Tests (obligatorio en main, opcional en desarrollo)
- Validación de secretos
- Validación de datos personales
- Formato de commits (Conventional Commits)
- Actualización automática de changelog

**Git Hooks:**
- `commit-msg`: Valida formato de commits
- `pre-push`: Verifica tests antes de push a main

**CI/CD Pipeline:**
- Validación completa en GitLab
- Tests obligatorios para merge a main
- Quality gate con cobertura mínima

### 3. Sistema de Commits

**Formato Conventional Commits:**
```
tipo(ámbito): descripción
```

**Tipos:**
- `feat`: Nueva funcionalidad → Incrementa MINOR
- `fix`: Corrección → Incrementa PATCH
- `docs`, `refactor`, `test`, `chore`: Mantenimiento

**Changelog Automático:**
- Actualización en cada commit
- Agrupación por categoría (Added, Fixed, Changed)
- Formato Keep a Changelog
- Versionado semántico

### 4. Flujo de Trabajo

```
Desarrollo → Pre-commit → Commit → Push → CI/CD → Merge
    ↓           ↓           ↓        ↓       ↓        ↓
  Tests     Validación  Changelog  Tests   Tests   Release
```

**Idempotencia:**
- Validaciones consistentes en local y CI
- Mismo resultado independiente de cuántas veces se ejecute
- Hooks automáticos garantizan cumplimiento

## Comandos Principales

```bash
# Configuración inicial
make setup-dev              # Configura todo el sistema

# Desarrollo
make dev                    # Servidor de desarrollo
make test                   # Tests completos
make lint                   # Linting
make format                 # Formateo

# Commits
make commit-wip             # Work-in-progress (sin tests)
make commit-safe            # Commit completo
git commit -m "tipo: desc"  # Manual con validación

# Changelog
make changelog              # Ver changelog
make changelog-unreleased   # Ver cambios pendientes

# Validación completa
make ci                     # Simular pipeline CI
```

## Reglas de Oro

1. **Commits en main**: Siempre con tests pasando
2. **Formato de commits**: Conventional Commits obligatorio
3. **Documentación**: LLMs piden autorización, humanos aprueban
4. **Secretos**: Detección automática, rechazo inmediato
5. **Changelog**: Actualización automática, no manual
6. **Idempotencia**: Mismas validaciones local y CI

## Beneficios

- **Consistencia**: Mismo flujo para todos los desarrolladores
- **Automatización**: Changelog y validaciones automáticas
- **Calidad**: Tests y linting obligatorios
- **Seguridad**: Detección de secretos y datos sensibles
- **Trazabilidad**: Historial claro con Conventional Commits
- **Colaboración**: Contrato claro LLM-Humano

## Mantenimiento

El sistema es auto-mantenible:
- Hooks se instalan automáticamente
- Changelog se actualiza automáticamente
- Validaciones se ejecutan automáticamente
- CI/CD verifica cumplimiento

Para actualizaciones del sistema, consultar con el equipo de desarrollo.