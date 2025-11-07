# Estado del Proyecto VUCE-SIDOM DAI

Última actualización: 2025-11-07

## Resumen Ejecutivo

**Proyecto**: DAI - Declaración Aduanera Integral
**Fase**: Análisis y desglose técnico del módulo D4
**Tareas listas**: 16 tareas en 5 historias de usuario
**Bloqueantes**: Integración con KIT Malvina/Maria

## Estado por Módulo

### D3 - Seguridad y Usuarios
**Estado**: Implementado (fuera del alcance actual)
- Autenticación vía Clave Fiscal ARCA
- Sistema de delegaciones CF4
- Roles y permisos

### D4 - Operaciones IMEX (DAI)
**Estado**: En análisis y desglose

#### Componentes Listos para Desarrollo (16 tareas)

**Dashboard (HU #21)**
- 3 tareas definidas
- Backend: Modelo de datos + API
- Frontend: Componente React

**Notificaciones (HU #127, #128)**
- 7 tareas definidas
- Activas: Modelo + API + Webhooks + Componente
- Históricas: Modelo + API + Vista

**Operaciones (HU #22, #23)**
- 6 tareas definidas
- Carga TXT: Componente + Parser + Job asíncrono
- Creación manual: Formulario + Endpoint + Sincronización catálogos

#### Componentes Completados (HU #129)

**Menú Lateral (HU #129)** - 8 tareas creadas
- Modelo de datos de configuración
- API de consulta según permisos
- Invalidación JIT de permisos
- Componente React dinámico
- Integración con sistema de permisos D3
- Actualización automática al cambiar CF4
- Tests E2E de navegación
- Diseño de integración con Adapter RPA

#### Componentes Pendientes de Desglose (1 historia)

**Pre-carátula PASO 1 (HU #125)**
- Historia creada sin tareas
- Posible duplicación con HU #23 (verificar)

#### Historias Duplicadas (1)

**Actualización Contextual (HU #130)**
- Duplicada con Tarea 6 de HU #129
- Acción: Marcar como duplicada y cerrar

#### Componentes Bloqueados

**Validaciones con KIT Malvina**
- HU #27: Consulta Bultos
- HU #28: Preguntas arancelarias
- Bloqueante: Falta especificación de integración

### D5 - Catálogo
**Estado**: Pendiente de análisis

### D6 - Búsqueda
**Estado**: Pendiente de análisis

### D7-D8 - Documentos
**Estado**: Pendiente de análisis

## Bloqueantes Críticos

### 1. Integración KIT Malvina/Maria
**Prioridad**: CRÍTICA
**Impacto**: Bloquea validaciones y oficialización
**Acción requerida**:
- Especificación de protocolo de comunicación
- Estructura de requests/responses
- Endpoints del Adapter .NET
- Documentación de errores y timeouts

**Solución temporal**: Crear mock/stub para desarrollo paralelo

### 2. Historias sin Desglosar
**Prioridad**: ALTA
**Impacto**: No se puede estimar ni asignar trabajo
**Acción requerida**:
- Desglosar HU #129 (Menú lateral)
- Desglosar HU #130 (Actualización contextual)
- Verificar HU #125 vs HU #23 (posible duplicación)

### 3. Historia Faltante
**Prioridad**: MEDIA
**Impacto**: Funcionalidad incompleta
**Acción requerida**:
- Crear HU-DAI-D4-006: Notificaciones históricas CF4

## Próximos Pasos

### Corto Plazo (1-2 semanas)
1. Verificar y desglosar HU #125 (Pre-carátula PASO 1)
2. Marcar HU #130 como duplicada en Taiga
3. Crear la historia faltante HU-DAI-D4-006
4. Define mock del KIT Malvina para desarrollo
5. Inicia desarrollo de las 24 tareas listas

### Mediano Plazo (3-4 semanas)
1. Completa implementación de Dashboard y Notificaciones
2. Obtiene especificación de integración con KIT Malvina
3. Implementa operaciones de creación manual y carga TXT
4. Integra menú lateral y cambio de contexto CF4

### Largo Plazo (2-3 meses)
1. Implementa validaciones con KIT Malvina
2. Completa flujo de oficialización
3. Integra con VUCE Central
4. Pruebas end-to-end completas

## Métricas

**Historias de Usuario**:
- Total en Taiga: 30
- Relacionadas con D4 Dashboard: 10
- Con tareas definidas: 6 (60%)
- Sin tareas: 1 (10%)
- Duplicadas: 1 (10%)
- Faltantes: 1 (10%)
- Pendientes verificación: 2 (20%)

**Tareas**:
- Listas para desarrollo: 24
- Estimadas: Pendiente
- En progreso: 0
- Completadas: 0

**Bloqueantes**:
- Críticos: 1 (KIT Malvina)
- Altos: 0
- Medios: 1 (Historia faltante)

## Recursos

**Documentación Técnica**:
- `util/vuce-sidom-architecture.md` - Arquitectura completa
- `util/kit-maria-integration.md` - Integración KIT Malvina
- `util/ejemplo-desglose-tareas.md` - Ejemplo real de desglose (HU #129)
- `util/llm-docs-proyect/taiga-hu-tasks-mapping.md` - Mapeo HU a tareas

**Datos de Taiga**:
- `util/llm-docs-proyect/taiga-*.json` - Snapshots de datos
- `util/llm-docs-proyect/TAIGA-DATA-README.md` - Guía de actualización

**Código**:
- `app/taiga_client.py` - Cliente de API Taiga
- `app/main.py` - Endpoints REST
- `README.md` - Guía de uso

## Contactos

**Equipo de Desarrollo**: Consultar con Fernando Piaggi
**VUCE/DGA**: Pendiente de definir contacto para especificación KIT Malvina
**Taiga**: https://taiga.vuce-sidom.gob.ar (proyecto DAI)
