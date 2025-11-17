# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed
- actualizar documentación con interfaz web interactiva y cambios recientes

Cambios en README.md:
- Reescritura completa con enfoque en funcionalidades actuales
- Sección destacada de features implementadas vs pendientes
- Guía completa de uso de interfaz /table-map
- Documentación detallada del editor de 3 tabs
- Issues pendientes documentados (gestión de épicas, tareas desde interfaz)
- Eliminada documentación obsoleta del flujo DAI
- Port actualizado a 8001
- Quick start simplificado en 4 pasos

Cambios en CHANGELOG.md:
- Nueva sección 'Added - Interfaz Web Interactiva (2025-01-16)'
- Documentación de visualización jerárquica Epic → US → Task
- Editor markdown con persistencia de drafts y sync bidireccional
- Control de versiones automático para prevenir conflictos
- Sección 'Changed' con mejoras de UX y backend
- Sección 'Fixed' con 5 fixes críticos documentados
- Metadata de commits analizados (29 commits, 10 días)

Features documentadas:
- Interfaz web /table-map con editor markdown completo
- 3 tabs: Source (editable), Vista Previa (tiempo real), HTML (Taiga)
- Persistencia en localStorage con carga/limpieza automática
- Control de versiones optimista con fetch de versión actual
- Renderizado Mermaid + syntax highlighting
- Gestión de tags con colores
- 8 nuevos endpoints de API

Commits analizados: 29 (período 2025-01-07 a 2025-01-16)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

# Please enter the commit message for your changes. Lines starting
# with '#' will be ignored, and an empty message aborts the commit.
#
# Date:      Sun Nov 16 21:29:18 2025 -0300
#
# On branch main
# Your branch is ahead of 'origin/main' by 2 commits.
#   (use "git push" to publish your local commits)
#
# Changes to be committed:
#	new file:   .codex/config.toml
#	modified:   .mcp.json
#	modified:   CHANGELOG.md
#	modified:   README.md
#	modified:   alembic/README
#	new file:   alembic/versions/4bb2e9540b5d_add_draft_board_table.py
#	modified:   alembic/versions/fc0a31b11810_initial_migration_with_project_epic_.py
#	modified:   app/ai_reorganizer.py
#	modified:   app/crud.py
#	modified:   app/main.py
#	modified:   app/models.py
#	modified:   app/schemas.py
#	modified:   app/sync_service.py
#	modified:   app/taiga_client.py
#	modified:   app/templates/table_map.html
#	modified:   pyproject.toml
#	new file:   scripts/fetch_stories_from_api.py
#	new file:   scripts/import_map_mvp.py
#	modified:   taiga_sync.db
#
# Changes not staged for commit:
#	modified:   app/sync_service.py
#
- actualizar documentación con interfaz web interactiva y cambios recientes

Cambios en README.md:
- Reescritura completa con enfoque en funcionalidades actuales
- Sección destacada de features implementadas vs pendientes
- Guía completa de uso de interfaz /table-map
- Documentación detallada del editor de 3 tabs
- Issues pendientes documentados (gestión de épicas, tareas desde interfaz)
- Eliminada documentación obsoleta del flujo DAI
- Port actualizado a 8001
- Quick start simplificado en 4 pasos

Cambios en CHANGELOG.md:
- Nueva sección 'Added - Interfaz Web Interactiva (2025-01-16)'
- Documentación de visualización jerárquica Epic → US → Task
- Editor markdown con persistencia de drafts y sync bidireccional
- Control de versiones automático para prevenir conflictos
- Sección 'Changed' con mejoras de UX y backend
- Sección 'Fixed' con 5 fixes críticos documentados
- Metadata de commits analizados (29 commits, 10 días)

Features documentadas:
- Interfaz web /table-map con editor markdown completo
- 3 tabs: Source (editable), Vista Previa (tiempo real), HTML (Taiga)
- Persistencia en localStorage con carga/limpieza automática
- Control de versiones optimista con fetch de versión actual
- Renderizado Mermaid + syntax highlighting
- Gestión de tags con colores
- 8 nuevos endpoints de API

Commits analizados: 29 (período 2025-01-07 a 2025-01-16)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

### Added - Interfaz Web Interactiva (2025-01-16)

**🎨 Interfaz Web `/table-map` - Editor Markdown Completo**

- **Visualización jerárquica completa**: Epic → User Story → Task en formato tabla interactiva
- **Editor markdown de 3 tabs**:
  - Tab "Source": Editor markdown editable
  - Tab "Vista Previa": Renderizado en tiempo real del markdown
  - Tab "HTML": HTML original de Taiga (actualizado al sincronizar)
- **Persistencia de drafts**: Guardado automático en localStorage del navegador
- **Sincronización bidireccional**:
  - 💾 Guardar en Draft (localStorage)
  - 🚀 Enviar a Taiga (sync remoto)
- **Control de versiones automático**:
  - Obtención de versión actual desde Taiga antes de actualizar
  - Prevención de conflictos de concurrencia
  - Mensajes de error claros para conflictos de versión
- **Renderizado avanzado**:
  - Diagramas Mermaid integrados
  - Syntax highlighting para código
  - Vista previa en tiempo real mientras escribes
- **Gestión de tags**: Agregar/visualizar tags con colores en User Stories
- **Navegación**: Botón "🚀 Taiga" para abrir elementos en Taiga web
- **Limpieza automática**: Drafts se eliminan automáticamente después de sincronizar exitosamente

**📡 Mejoras de API**

- GET `/table-map?project=<id>` - Nueva interfaz web interactiva
- Endpoint GET `/user-stories/{id}` ahora incluye `taiga_id` y `version` en respuesta
- Endpoint GET `/tasks/{id}` incluye `taiga_id` para sincronización
- PATCH `/user-stories/{id}` con control de versiones optimista
- PATCH `/tasks/{id}` con control de versiones optimista
- POST `/epics` para crear épicas (endpoint existente)
- GET `/epics?project=<id>` con modo verbose y user stories anidadas
- GET `/project-map` para obtener estructura jerárquica completa
- POST `/auth/token` para cambiar token sin reiniciar servidor
- GET `/projects/{id}/milestones` - Listado de sprints/milestones
- GET `/projects/{id}/tags` - Tags del proyecto con colores

**🔧 Mejoras Técnicas**

- Serialización mejorada en `_build_story_details()`: ahora incluye `taiga_id` y `version`
- Template HTML `table_map.html` con ~4500 líneas de código JavaScript
- Integración de librerías:
  - marked.js v11.1.1 para parsing de markdown
  - mermaid.js v10 para diagramas
  - Sortable.js para drag & drop (futuro)
- Manejo robusto de errores con mensajes user-friendly
- Logs detallados en consola para debugging

**📚 Documentación Actualizada (2025-01-16)**

- README.md completamente reescrito:
  - Sección destacada de funcionalidades implementadas vs pendientes
  - Guía completa de uso de la interfaz `/table-map`
  - Documentación de los 3 tabs del editor
  - Ejemplos de uso típico paso a paso
  - Eliminada documentación obsoleta del flujo DAI
  - Port actualizado a 8001
- Issues pendientes documentados:
  - Gestión de épicas desde interfaz
  - Creación/modificación de tareas desde interfaz
  - Sincronización avanzada de épicas completas
  - Mejoras de interfaz (drag & drop, filtros)

### Changed
- actualizar documentación con interfaz web interactiva y cambios recientes

Cambios en README.md:
- Reescritura completa con enfoque en funcionalidades actuales
- Sección destacada de features implementadas vs pendientes
- Guía completa de uso de interfaz /table-map
- Documentación detallada del editor de 3 tabs
- Issues pendientes documentados (gestión de épicas, tareas desde interfaz)
- Eliminada documentación obsoleta del flujo DAI
- Port actualizado a 8001
- Quick start simplificado en 4 pasos

Cambios en CHANGELOG.md:
- Nueva sección 'Added - Interfaz Web Interactiva (2025-01-16)'
- Documentación de visualización jerárquica Epic → US → Task
- Editor markdown con persistencia de drafts y sync bidireccional
- Control de versiones automático para prevenir conflictos
- Sección 'Changed' con mejoras de UX y backend
- Sección 'Fixed' con 5 fixes críticos documentados
- Metadata de commits analizados (29 commits, 10 días)

Features documentadas:
- Interfaz web /table-map con editor markdown completo
- 3 tabs: Source (editable), Vista Previa (tiempo real), HTML (Taiga)
- Persistencia en localStorage con carga/limpieza automática
- Control de versiones optimista con fetch de versión actual
- Renderizado Mermaid + syntax highlighting
- Gestión de tags con colores
- 8 nuevos endpoints de API

Commits analizados: 29 (período 2025-01-07 a 2025-01-16)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

# Please enter the commit message for your changes. Lines starting
# with '#' will be ignored, and an empty message aborts the commit.
#
# Date:      Sun Nov 16 21:29:18 2025 -0300
#
# On branch main
# Your branch is ahead of 'origin/main' by 2 commits.
#   (use "git push" to publish your local commits)
#
# Changes to be committed:
#	new file:   .codex/config.toml
#	modified:   .mcp.json
#	modified:   CHANGELOG.md
#	modified:   README.md
#	modified:   alembic/README
#	new file:   alembic/versions/4bb2e9540b5d_add_draft_board_table.py
#	modified:   alembic/versions/fc0a31b11810_initial_migration_with_project_epic_.py
#	modified:   app/ai_reorganizer.py
#	modified:   app/crud.py
#	modified:   app/main.py
#	modified:   app/models.py
#	modified:   app/schemas.py
#	modified:   app/sync_service.py
#	modified:   app/taiga_client.py
#	modified:   app/templates/table_map.html
#	modified:   pyproject.toml
#	new file:   scripts/fetch_stories_from_api.py
#	new file:   scripts/import_map_mvp.py
#	modified:   taiga_sync.db
#
# Changes not staged for commit:
#	modified:   app/sync_service.py
#

- **Backend**: `_serialize()` en `main.py` ahora incluye `taiga_id` y `version` para User Stories y Tasks
- **Frontend**: Editor visible por defecto (sin botón "Editar")
- **Frontend**: Tab "Vista Previa" activa por defecto (mejor UX)
- **Frontend**: Colores de tabs mejorados para mejor visibilidad
  - Tab activo: fondo blanco, borde azul (#3b82f6)
  - Tab inactivo: fondo gris (#f3f4f6), texto gris (#6b7280)
- **Frontend**: Botones de acción con colores distintivos
  - 💾 Draft: amarillo (#fbbf24)
  - 🚀 Taiga: verde (#10b981)
- **API**: Control de versiones ahora obtiene versión actual de Taiga antes de actualizar

### Fixed

- **Fix crítico**: Conflictos de versión en actualización de User Stories y Tasks
  - Ahora se obtiene la versión actual desde Taiga antes de PATCH
  - Previene error 400 "version doesn't match"
- **Fix**: Editor de textarea ahora es editable correctamente
  - Eliminado `cloneNode()` que causaba pérdida de propiedades
  - Uso de flag `dataset.listenerAttached` para prevenir listeners duplicados
- **Fix**: Panel HTML se actualiza correctamente después de sincronizar con Taiga
  - Incluye renderizado de diagramas Mermaid en HTML
- **Fix**: Drafts persisten correctamente en localStorage
  - Carga automática al abrir modal
  - Limpieza automática después de sync exitoso
- **Fix**: Mensajes de error más claros para conflictos de versión
  - Instrucciones paso a paso para resolver el conflicto

### Added - Features Previos
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
- actualizar documentación con interfaz web interactiva y cambios recientes

Cambios en README.md:
- Reescritura completa con enfoque en funcionalidades actuales
- Sección destacada de features implementadas vs pendientes
- Guía completa de uso de interfaz /table-map
- Documentación detallada del editor de 3 tabs
- Issues pendientes documentados (gestión de épicas, tareas desde interfaz)
- Eliminada documentación obsoleta del flujo DAI
- Port actualizado a 8001
- Quick start simplificado en 4 pasos

Cambios en CHANGELOG.md:
- Nueva sección 'Added - Interfaz Web Interactiva (2025-01-16)'
- Documentación de visualización jerárquica Epic → US → Task
- Editor markdown con persistencia de drafts y sync bidireccional
- Control de versiones automático para prevenir conflictos
- Sección 'Changed' con mejoras de UX y backend
- Sección 'Fixed' con 5 fixes críticos documentados
- Metadata de commits analizados (29 commits, 10 días)

Features documentadas:
- Interfaz web /table-map con editor markdown completo
- 3 tabs: Source (editable), Vista Previa (tiempo real), HTML (Taiga)
- Persistencia en localStorage con carga/limpieza automática
- Control de versiones optimista con fetch de versión actual
- Renderizado Mermaid + syntax highlighting
- Gestión de tags con colores
- 8 nuevos endpoints de API

Commits analizados: 29 (período 2025-01-07 a 2025-01-16)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>

# Please enter the commit message for your changes. Lines starting
# with '#' will be ignored, and an empty message aborts the commit.
#
# Date:      Sun Nov 16 21:29:18 2025 -0300
#
# On branch main
# Your branch is ahead of 'origin/main' by 2 commits.
#   (use "git push" to publish your local commits)
#
# Changes to be committed:
#	new file:   .codex/config.toml
#	modified:   .mcp.json
#	modified:   CHANGELOG.md
#	modified:   README.md
#	modified:   alembic/README
#	new file:   alembic/versions/4bb2e9540b5d_add_draft_board_table.py
#	modified:   alembic/versions/fc0a31b11810_initial_migration_with_project_epic_.py
#	modified:   app/ai_reorganizer.py
#	modified:   app/crud.py
#	modified:   app/main.py
#	modified:   app/models.py
#	modified:   app/schemas.py
#	modified:   app/sync_service.py
#	modified:   app/taiga_client.py
#	modified:   app/templates/table_map.html
#	modified:   pyproject.toml
#	new file:   scripts/fetch_stories_from_api.py
#	new file:   scripts/import_map_mvp.py
#	modified:   taiga_sync.db
#
# Changes not staged for commit:
#	modified:   app/sync_service.py
#
- update with latest API changes

Update CHANGELOG with epic endpoints, dynamic auth, milestones and tags features

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
- add epic endpoints with verbose mode, dynamic auth, milestones and tags

- Add GET /epics endpoint with EpicResponse schema
- Add GET /epics/{epic_id} with verbose mode for full details
- Add dynamic bearer token auth via POST /auth/token
- Modify GET /debug/connection to return AuthStatusResponse
- Add GET /projects/{project_id}/milestones endpoint
- Add GET /projects/{project_id}/tags endpoint
- Add UserStoryDetailResponse schema with task inclusion
- Add tag normalization with field_validator (flatten nested lists)
- Add ConfigDict(extra='allow') to accept all Taiga API fields
- Add fastapi-mcp dependency for MCP integration
- Add API documentation with endpoints, schemas, and code statistics

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
- docs(d5): documentar catálogo D5 y actualizar referencias

Cambios incluidos:
- documentar catálogo D5 y actualizar referencias

- Crear util/d5-catalogo-documentacion.md con modelo completo
  - 4 entidades: NCM, ITEM, SUBITEM, CATALOGO_CAMPO
  - Diagramas ER en Mermaid
  - Relaciones, validaciones y casos de uso
  - Verificado contra DER en VUCE-Modelo de datos.drawio.xml

- Actualizar referencias en toda la documentación
  - util/vuce-sidom-architecture.md: agregar modelo D5
  - util/project-status.md: métricas actualizadas (16 HU, 102 tareas)
  - util/kit-maria-integration.md: HU afectadas y referencias
  - README.md: documentación de módulos
  - util/README.md: árbol actualizado

- Documentar fuentes de información
  - Google Drive SIDOM (Historias de Usuario, TASKs D3)
  - Taiga (snapshots JSON en util/llm-docs-proyect/)
  - Decisiones pendientes marcadas como SIDOM/DGA

- Archivos DrawIO ubicados correctamente
  - util/llm-docs-proyect/graficos.drawio.xml (597K)
  - util/llm-docs-proyect/VUCE-Modelo de datos.drawio.xml (512K)
- actualizar README con estructura completa del proyecto

- Árbol completo del proyecto con todos los archivos y carpetas
- Descripción detallada de app/, tests/, scripts/ y util/
- Documentación de llm-docs-proyect/ con índice de contenidos
- Actualizar propósito con nuevas funcionalidades (CRUD completo)
- Ampliar tecnologías clave con herramientas de desarrollo
- Mejorar configuración crítica con opciones de autenticación
- Comandos esenciales actualizados con scripts y workflows
- actualizar changelog con cambios de documentación
- documentar endpoints POST y PATCH para user-stories
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

**Última actualización manual**: 2025-01-16 - Consolidación de cambios de interfaz web interactiva

**Commits analizados**: 29 commits de los últimos 10 días (2025-01-07 a 2025-01-16)

**Nota**: Este changelog se actualiza automáticamente mediante hooks de pre-commit para cambios menores. Las actualizaciones mayores se documentan manualmente.
