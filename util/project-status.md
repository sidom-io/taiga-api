# Estado del Proyecto VUCE-SIDOM DAI

Última actualización: 2025-11-07

## Resumen Ejecutivo

**Proyecto**: DAI - Declaración Aduanera Integral
**Fase**: Análisis y desglose técnico del módulo D4
**Historias de Usuario D4**: 16 historias, 102 tareas (85% completo)
**Bloqueantes**: Integración con KIT Malvina/Maria

**Fuente de Información**:
- Documentación en Google Drive de SIDOM (acceso mediante cache local)
- Sincronización con Taiga: `util/llm-docs-proyect/` (ver README.md para métricas actualizadas)
- Historias de Usuario y TASKs: Documentos Word y archivos JSON de Taiga

## Estado por Módulo

**Nota**: Para métricas detalladas y estado actualizado de sincronización con Taiga, ver `util/llm-docs-proyect/README.md`

### D3 - Seguridad y Usuarios
**Estado**: ✅ Completo (8 historias, 54 tareas)
- Autenticación vía Clave Fiscal ARCA
- Sistema de delegaciones CF4
- Roles y permisos
- Backoffice de administración

### D4 - Operaciones IMEX (DAI)
**Estado**: ✅ 85% Completo (16 historias, 102 tareas)

**Fuente**: Documentación SIDOM en Google Drive (cache local en `util/llm-docs-proyect/`)

#### Historias Completadas con Tareas Definidas

| HU | Título | Tareas | Archivo Desglose |
|----|--------|--------|------------------|
| #21 | Ver el dashboard | 3 | - |
| #22 | Crear desde TXT | 3 | - |
| #23 | PASO 0: Iniciar DAI | 3 | `tareas-hu23-paso0-iniciar.md` |
| #24 | PASO 2: Carátula | 4 | - |
| #25 | PASO 3: Items/Subitems | 6 | - |
| #26 | PASO 4: Docs Exportación | 8 | `tareas-hu26-paso4-validacion-docs.md` |
| #27 | PASO 5: Bultos | 8 | `tareas-hu27-paso5-bultos.md` |
| #28 | PASO 6: Presupuesto | 9 | `tareas-hu28-paso6-presupuesto.md` |
| #125 | PASO 1: Pre-Carátula | 8 | `tareas-hu125-paso1-precaratula.md` |
| #126 | Carga masiva CSV | 9 | `tareas-hu126-carga-masiva-csv.md` |
| #127 | Notificaciones activas | 4 | - |
| #128 | Notificaciones históricas | 8 | `tareas-hu128-notif-historicas-mejoradas.md` |
| #129 | Menú lateral dinámico | 8 | `tareas-hu129-menu-lateral.md` |
| #241 | Pago de tributos con VEP | 7 | `tareas-hu-pago-vep.md` |
| #251 | Asociación pólizas/cauciones | 7 | `tareas-hu-polizas-cauciones.md` |
| #259 | Liquidación y oficialización | 7 | `bulk-tareas-oficializacion.md` |

**Total**: 16 historias, 102 tareas

#### Historias Duplicadas

**HU #130 (Actualización Contextual)**
- Duplicada con Tarea 6 de HU #129
- Acción: Marcar como duplicada en Taiga

#### Historias Adicionales Propuestas (Pendientes de Validación SIDOM)

| HU Propuesta | Título | Prioridad | Estado |
|--------------|--------|-----------|--------|
| HU-DAI-D4-013 | Consulta de estado de operaciones | Media | 📋 Por validar con SIDOM |
| HU-DAI-D4-014 | Modificación de DAI (Rectificativa) | Media | 📋 Por validar con SIDOM |
| HU-DAI-D4-015 | Anulación de operaciones | Media | 📋 Por validar con SIDOM |

**Documentación**: Ver `util/llm-docs-proyect/historias-d4-faltantes.md`

### D5 - Catálogo
**Estado**: Modelo de datos documentado, pendiente de implementación

**Modelo de Datos Definido:**
- NCM (Nomenclatura Común del Mercosur)
- ITEM (Mercaderías en declaraciones)
- SUBITEM (Detalle de cantidades y valores)
- CATALOGO_CAMPO (Campos dinámicos por subrégimen)

**Documentación**: `util/d5-catalogo-documentacion.md`

**Próximos Pasos:**
1. Crear historias de usuario para D5
2. Implementar modelo de datos en base de datos
3. Desarrollar APIs de consulta de NCM
4. Implementar gestión de campos dinámicos
5. Integrar con módulo D4

### D6 - Búsqueda
**Estado**: Pendiente de análisis

### D7-D8 - Documentos
**Estado**: Pendiente de análisis

## Bloqueantes Críticos

**Fuente de Bloqueantes**: Documentación SIDOM (Google Drive) - Secciones "Detalles sujetos a validación"

### 1. Integración KIT Malvina/Maria
**Prioridad**: CRÍTICA
**Impacto**: Bloquea validaciones y oficialización
**Decisión requerida de**: SIDOM/DGA
**Acción requerida**:
- Especificación de protocolo de comunicación
- Estructura de requests/responses
- Endpoints del Adapter .NET
- Documentación de errores y timeouts

**Solución temporal**: Crear mock/stub para desarrollo paralelo
**Documentación**: `util/kit-maria-integration.md`

### 2. Catálogos y Validaciones (Pendientes SIDOM)
**Prioridad**: ALTA
**Decisión requerida de**: SIDOM
**Acción requerida**:
- Catálogo completo de tipos de eventos para notificaciones
- Matriz de permisos por rol
- Política de retención de notificaciones históricas
- Formatos de documentos por país (PASO 4)
- Diagrama completo de transición de estados

### 3. Historias Adicionales Propuestas
**Prioridad**: MEDIA
**Decisión requerida de**: SIDOM
**Acción requerida**:
- Validar si se requieren HU-DAI-D4-013, 014, 015
- Definir alcance de consultas, modificaciones y anulaciones

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

**Fuente**: Sincronización con Taiga (ver `util/llm-docs-proyect/README.md` para detalle completo)

**Por Épica**:

| Épica | Historias | Tareas | Estado |
|-------|-----------|--------|--------|
| D3 - Gestión usuario | 8 | 54 | ✅ Completo |
| D4 - Declaración aduanera | 16 | 102 | ✅ 85% completo |
| Backoffice | 3 | 23 | ✅ Completo |
| **Total** | **33** | **179** | **85% completo** |

**Historias de Usuario D4**:
- Total en Taiga: 16
- Con tareas definidas: 16 (100%)
- Duplicadas: 1 (HU #130)
- Propuestas pendientes validación SIDOM: 3

**Tareas D4**:
- Total definidas: 102
- Listas para desarrollo: 102
- Estimadas: Pendiente
- En progreso: 0
- Completadas: 0

**Bloqueantes**:
- Críticos: 1 (KIT Malvina - decisión SIDOM)
- Altos: 1 (Catálogos - decisión SIDOM)
- Medios: 1 (Historias adicionales - validación SIDOM)

## Recursos

**Documentación Técnica**:
- `util/vuce-sidom-architecture.md` - Arquitectura completa
- `util/d5-catalogo-documentacion.md` - Modelo de datos D5 (Catálogo)
- `util/kit-maria-integration.md` - Integración KIT Malvina
- `util/ejemplo-desglose-tareas.md` - Ejemplo real de desglose (HU #129)

**Documentación Privada (Google Drive SIDOM - cache local)**:
- `util/llm-docs-proyect/README.md` - **Estado actualizado y métricas completas**
- `util/llm-docs-proyect/taiga-hu-tasks-mapping.md` - Mapeo épicas/HU/tareas
- `util/llm-docs-proyect/historias-d4-faltantes.md` - Historias propuestas
- `util/llm-docs-proyect/graficos.drawio.xml` - Diagramas (flujos, estados, DER)
- `util/llm-docs-proyect/VUCE-Modelo de datos.drawio.xml` - DER completo
- `util/llm-docs-proyect/tareas-hu*.md` - Desgloses técnicos por HU
- `util/llm-docs-proyect/bulk-tareas-*.md` - Archivos para carga en Taiga

**Datos de Taiga (Snapshots JSON)**:
- `util/llm-docs-proyect/taiga-*.json` - Snapshots de HU y tareas
- `util/llm-docs-proyect/TAIGA-DATA-README.md` - Guía de actualización

**Código**:
- `app/taiga_client.py` - Cliente de API Taiga
- `app/main.py` - Endpoints REST
- `README.md` - Guía de uso

## Contactos

**Equipo de Desarrollo**: Consultar con Fernando Piaggi
**VUCE/DGA**: Pendiente de definir contacto para especificación KIT Malvina
**Taiga**: https://taiga.vuce-sidom.gob.ar (proyecto DAI)
