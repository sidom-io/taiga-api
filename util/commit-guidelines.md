# Guías de Commits y Versionado

## Formato de Commits

Este proyecto utiliza [Conventional Commits](https://www.conventionalcommits.org/) para mantener un historial claro y generar changelogs automáticamente.

### Estructura

```
<tipo>[ámbito opcional]: <descripción>

[cuerpo opcional]

[pie opcional]
```

### Tipos de Commit

- **feat**: Nueva funcionalidad
- **fix**: Corrección de errores
- **docs**: Cambios en documentación
- **style**: Cambios de formato (espacios, comas, etc.)
- **refactor**: Refactorización de código
- **test**: Agregar o modificar tests
- **chore**: Tareas de mantenimiento
- **perf**: Mejoras de rendimiento
- **ci**: Cambios en CI/CD
- **build**: Cambios en sistema de build

### Ejemplos

```bash
feat(auth): agregar soporte para tokens de sesión del navegador
fix(client): corregir manejo de errores de conexión
docs(readme): actualizar instrucciones de instalación
test(client): agregar tests para autenticación
chore(deps): actualizar dependencias de desarrollo
```

### Ámbitos Comunes

- **auth**: Autenticación y autorización
- **client**: Cliente de Taiga
- **api**: Endpoints de FastAPI
- **docs**: Documentación
- **test**: Tests y validaciones
- **ci**: Pipeline CI/CD
- **dev**: Herramientas de desarrollo

## Versionado Semántico

### Formato: MAJOR.MINOR.PATCH

- **MAJOR**: Cambios incompatibles en la API
- **MINOR**: Nueva funcionalidad compatible
- **PATCH**: Correcciones compatibles

### Reglas de Incremento

- **feat**: Incrementa MINOR
- **fix**: Incrementa PATCH
- **BREAKING CHANGE**: Incrementa MAJOR
- **chore, docs, style, test**: No incrementan versión

## Proceso Automático

### En Cada Commit

```bash
git commit -m "feat(auth): agregar nueva funcionalidad"
```

Automáticamente se ejecuta:
1. **Pre-commit**: Formato, linting, validaciones
2. **Prepare-commit-msg**: Actualiza CHANGELOG.md
3. **Commit-msg**: Valida formato Conventional Commits
4. **Commit**: Se completa con changelog actualizado

### Changelog Automático

El CHANGELOG.md se actualiza automáticamente según el tipo de commit:
- `feat` → Sección "Added"
- `fix` → Sección "Fixed"
- Otros → Sección "Changed"

**No es necesario editar CHANGELOG.md manualmente**

### Proceso de Release

1. **Desarrollo**: Commits en ramas feature (changelog se actualiza automáticamente)
2. **Merge**: A main con todos los tests pasando
3. **Tag**: Creación manual de versión cuando sea necesario

## Comandos Útiles

```bash
# Commit normal (todo automático)
git commit -m "feat(scope): descripción"

# Omitir tests en ramas de desarrollo
SKIP_TESTS=1 git commit -m "feat: trabajo en progreso"

# Ver changelog generado
cat CHANGELOG.md
head -30 CHANGELOG.md

# Ver historial de commits
git log --oneline -10

# Verificar formato de último commit
git log -1 --pretty=format:%s
```
