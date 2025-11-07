# Troubleshooting: uv y Python 3.13

Guía técnica para resolver errores comunes al usar `uv` con Python 3.13+.

## Error: ModuleNotFoundError: No module named '_distutils_hack'

### Síntomas

```
Error processing line 1 of .venv/lib/python3.13/site-packages/distutils-precedence.pth:
  Traceback (most recent call last):
    File "<frozen site>", line 206, in addpackage
    File "<string>", line 1, in <module>
  ModuleNotFoundError: No module named '_distutils_hack'
```

### Causa

Python 3.13 tiene cambios en la gestión de `setuptools` y `distutils`. El archivo `distutils-precedence.pth` puede quedar corrupto o incompatible.

### Diagnóstico

Verificar el path de Python usando `uv`:

```bash
# Verificar ubicación del ejecutable
uv run which python

# Verificar versión
uv run python --version

# Verificar path completo (puede mostrar el error)
uv run python -c "import sys; print(sys.executable)"
```

### Solución

**Paso 1: Eliminar archivo problemático**

```bash
rm -f .venv/lib/python3.13/site-packages/distutils-precedence.pth
```

**Paso 2: Verificar que el error desapareció**

```bash
uv run python -c "import sys; print('✅ Python OK:', sys.executable)"
```

**Paso 3: Reinstalar dependencias si es necesario**

Si las herramientas de desarrollo desaparecieron:

```bash
# Sincronizar entorno completo
uv sync --dev

# O instalar herramientas específicas
uv pip install black isort flake8 pylint pytest
```

## Error: Herramientas de desarrollo no encontradas

### Síntomas

```
/path/to/.venv/bin/python3: No module named black
/path/to/.venv/bin/python3: No module named isort
```

### Causa

Las dependencias de desarrollo no están instaladas o se desinstalaron durante una operación de mantenimiento.

### Solución

```bash
# Opción 1: Sincronizar con pyproject.toml
uv sync --dev

# Opción 2: Instalar manualmente
uv pip install black isort flake8 pylint pytest

# Verificar instalación
uv pip list | grep -E "(black|isort|flake8|pylint)"
```

## Error: Imports no utilizados en flake8

### Síntomas

```
file.py:3:1: F401 'module.Class' imported but unused
```

### Solución

Eliminar imports no utilizados del archivo. Ejemplo:

```python
# Antes
from unittest.mock import AsyncMock, patch
from app.module import Class1, Class2, Class3

# Después (solo lo que se usa)
from app.module import Class1
```

## Verificación de entorno con uv

### Comandos útiles

```bash
# Listar paquetes instalados
uv pip list

# Verificar path de Python
uv run which python

# Ejecutar comando en el entorno
uv run <comando>

# Sincronizar entorno completo
uv sync --dev

# Reinstalar paquete específico
uv sync --reinstall-package <paquete>
```

## Pre-commit hooks con uv

Si usas pre-commit con `uv`, asegúrate de que los hooks usen `uv run`:

```yaml
- repo: local
  hooks:
    - id: black
      name: Formatear código con Black
      entry: uv run python -m black
      language: system
      types: [python]
```

## Mejores prácticas

1. **Siempre usar `uv run`** para ejecutar comandos en el entorno virtual
2. **Verificar instalación** después de operaciones de mantenimiento
3. **Eliminar archivos .pth corruptos** en lugar de recrear todo el entorno
4. **Mantener pyproject.toml actualizado** con todas las dependencias
5. **Usar `uv sync --dev`** para asegurar consistencia del entorno

## Recursos

- [uv Documentation](https://github.com/astral-sh/uv)
- [Python 3.13 Release Notes](https://docs.python.org/3.13/whatsnew/3.13.html)
- [setuptools Documentation](https://setuptools.pypa.io/)
