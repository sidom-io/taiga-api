# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- agregar endpoint para listar proyectos
- agregar sistema de análisis de cambios con LLM
- agregar actualización automática de changelog
- Sistema de pre-commit hooks con validaciones completas
- Pipeline CI/CD para GitLab con múltiples etapas de validación
- Configuración de desarrollo automatizada con scripts
- Tests unitarios básicos para FastAPI y cliente Taiga
- Sistema de documentación estructurado en util/
- Contrato LLM-Humano para manejo de documentación
- Makefile con comandos de desarrollo comunes
- Soporte para omitir tests en ramas de desarrollo (SKIP_TESTS=1)

### Changed
- agregar endpoints para gestión completa de tareas y proyectos

- Agregar métodos al cliente: get_project, get_task, list_tasks, update_task
- Agregar endpoints de metadatos: task-statuses, userstory-statuses
- Implementar filtrado de tareas por proyecto, historia, estado y asignado
- Agregar endpoint PATCH para actualizar tareas
- Actualizar README con nuevos endpoints y ejemplos de uso

Endpoints nuevos:
- GET /projects/{id} - Detalle de proyecto
- GET /tasks - Listar tareas con filtros
- GET /tasks/{id} - Detalle de tarea
- PATCH /tasks/{id} - Actualizar tarea
- GET /projects/{id}/task-statuses - Estados de tareas
- GET /projects/{id}/userstory-statuses - Estados de historias
- agregar endpoints para gestión completa de tareas y proyectos

- Agregar métodos al cliente: get_project, get_task, list_tasks, update_task
- Agregar endpoints de metadatos: task-statuses, userstory-statuses
- Implementar filtrado de tareas por proyecto, historia, estado y asignado
- Agregar endpoint PATCH para actualizar tareas
- Actualizar README con nuevos endpoints y ejemplos de uso

Endpoints nuevos:
- GET /projects/{id} - Detalle de proyecto
- GET /tasks - Listar tareas con filtros
- GET /tasks/{id} - Detalle de tarea
- PATCH /tasks/{id} - Actualizar tarea
- GET /projects/{id}/task-statuses - Estados de tareas
- GET /projects/{id}/userstory-statuses - Estados de historias
- actualizar contexto del proyecto
- agregar guía de troubleshooting para uv y Python 3.13
- verificar funcionamiento después de fix
- actualizar documentación con flujo de trabajo simplificado
- Actualizada configuración de pyproject.toml con dependencias de desarrollo
- Mejorada documentación con separación clara de responsabilidades
- Optimizada configuración de herramientas (Black, Flake8, Pylint, MyPy)

### Security
- Implementada detección automática de secretos en pre-commit
- Validación de datos personales para prevenir commits accidentales
- Configuración de .gitignore para proteger archivos sensibles

## [0.1.0] - 2024-11-07

### Added
- agregar endpoint para listar proyectos
- agregar sistema de análisis de cambios con LLM
- agregar actualización automática de changelog
- Servicio FastAPI asíncrono para integración con Taiga
- Cliente HTTP asíncrono con cache de tokens
- Soporte para autenticación por token de sesión del navegador
- Soporte alternativo para autenticación usuario/contraseña
- Endpoints de diagnóstico para troubleshooting
- Documentación completa de configuración y uso
- Esquemas Pydantic para validación de datos
- Configuración con variables de entorno

### Features
- Crear tareas en Taiga via API REST
- Listar historias de usuario con filtros
- Obtener detalles de historias específicas
- Listar tareas asociadas a historias
- Cache inteligente de tokens de autenticación
- Manejo robusto de errores y reconexión

---

**Nota**: Este changelog se actualiza automáticamente mediante hooks de pre-commit.
