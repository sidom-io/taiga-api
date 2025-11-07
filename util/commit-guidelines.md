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

## Proceso de Release

1. **Desarrollo**: Commits en ramas feature
2. **Pre-commit**: Validaciones automáticas
3. **Merge**: A main con todos los tests pasando
4. **Changelog**: Actualización automática
5. **Tag**: Creación automática de versión

## Hooks Automáticos

### Pre-commit
- Validación de formato de commit
- Actualización de CHANGELOG.md
- Ejecución de tests (obligatorio en main)
- Linting y formateo

### Post-commit
- Actualización de versión en pyproject.toml
- Generación de tags automáticos

## Comandos Útiles

```bash
# Commit con validación completa
make commit-safe

# Commit work-in-progress (sin tests)
make commit-wip

# Verificar formato antes de commit
git log --oneline -10

# Ver changelog generado
cat CHANGELOG.md
```