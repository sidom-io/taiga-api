# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- agregar endpoints para crear y actualizar historias de usuario
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
- implementar creación bulk de tareas desde markdown y completar HU #129

Funcionalidades nuevas:
- Parser de markdown para extraer tareas con criterios y dependencias
- Endpoint POST /tasks/bulk-from-markdown para creación masiva
- Conversión automática de referencias (Tarea N, HU #N) a links de Taiga
- Actualización automática de descripción de US con diagramas
- Endpoint DELETE /tasks/{id} para eliminar tareas
- Método update_user_story para actualizar historias

HU #129 - Menú Lateral Dinámico:
- 8 tareas creadas en Taiga (#175-#182)
- Diagramas Mermaid de arquitectura y flujo
- Tarea 3 modificada: Invalidación JIT en lugar de caché simple
- Incluye integración con Adapter RPA (tarea paralela)

Documentación:
- util/ejemplo-desglose-tareas.md - Ejemplo real basado en HU #129
- HU #130 marcada como duplicada (redundante con Tarea 6 de HU #129)
- Actualizado project-status.md: 6 historias completas, 24 tareas
- Actualizado taiga-hu-tasks-mapping.md con estado actual

Total: 24 tareas listas para desarrollo
- agregar tabla comparativa HU vs tareas y cache de datos

- Crear tabla comparativa completa de HU del documento vs tareas en Taiga
- Identificar 16 tareas listas para desarrollo en 5 historias
- Detectar 3 historias sin desglosar que necesitan tareas
- Cachear datos de Taiga en archivos JSON para consulta offline
- Agregar README de datos con instrucciones de actualización

Archivos de cache creados:
- taiga-projects-list.json
- taiga-user-stories-dai.json
- taiga-tasks-us*.json (10 historias)
- taiga-task-statuses.json
- taiga-userstory-statuses.json
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
- agregar endpoints para crear y actualizar historias de usuario
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
