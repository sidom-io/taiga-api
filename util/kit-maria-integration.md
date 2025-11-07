# Integración con KIT Malvina/Maria

## Descripción

KIT Malvina (también conocido como KIT Maria) es el sistema legacy de la Dirección General de Aduanas de Argentina utilizado para:

- Validaciones arancelarias
- Cálculo de tributos aduaneros
- Verificación de posiciones NCM
- Aplicación de regímenes especiales

## Arquitectura de Integración

```
Backend FastAPI
    ↓
RabbitMQ (Message Queue)
    ↓
Adapter .NET (x86) - VM Windows
    ↓
KIT Malvina (Aplicación 32-bit)
    ↓
Adapter .NET (Webhook)
    ↓
Backend FastAPI
```

## Componentes

### Adapter .NET

**Propósito**: Automatizar la interfaz gráfica del KIT Malvina (sistema legacy sin API).

**Características:**
- Aplicación .NET C# compilada para x86 (32-bit)
- Corre en máquinas virtuales Windows
- Múltiples instancias para escalabilidad
- Consume mensajes de RabbitMQ
- Envía respuestas vía webhook al backend

**Funcionalidades:**
- Automatización de UI del KIT Malvina
- Extracción de datos de pantallas
- Simulación de entrada de usuario
- Captura de resultados y errores

### RabbitMQ

**Propósito**: Desacoplar el backend del Adapter para procesamiento asíncrono.

**Ventajas:**
- Tolerancia a fallos
- Escalabilidad horizontal
- Retry automático
- Priorización de mensajes

## ⚠️ Información Pendiente (Bloqueante Crítico)

### 1. Protocolo de Comunicación

**Necesitamos definir:**

- ¿Qué formato de mensaje usa RabbitMQ?
  ```json
  {
    "operation_id": "string",
    "action": "validate|calculate|query",
    "data": {}
  }
  ```

- ¿Qué estructura tiene el webhook de respuesta?
  ```json
  {
    "operation_id": "string",
    "status": "success|error",
    "result": {},
    "errors": []
  }
  ```

### 2. Endpoints del Adapter

**Necesitamos documentar:**

- URL base del webhook
- Autenticación requerida
- Headers necesarios
- Timeout esperado
- Manejo de reintentos

### 3. Operaciones Disponibles

**Validaciones:**
- ¿Cómo validar una posición arancelaria?
- ¿Qué datos se requieren?
- ¿Qué respuesta se obtiene?

**Cálculo de Tributos:**
- ¿Qué información se envía?
- ¿Cómo se estructura la respuesta?
- ¿Incluye desglose de tributos?

**Consultas:**
- ¿Se pueden consultar datos históricos?
- ¿Hay caché de resultados?

### 4. Estructura de Datos

**Request típico (ejemplo hipotético):**
```json
{
  "operation_id": "DAI-2025-001234",
  "action": "calculate_tributes",
  "data": {
    "ncm_code": "8471.30.12",
    "origin_country": "CN",
    "fob_value": 10000.00,
    "currency": "USD",
    "regime": "IMPORTACION_DEFINITIVA",
    "customs_office": "EZEIZA"
  }
}
```

**Response típico (ejemplo hipotético):**
```json
{
  "operation_id": "DAI-2025-001234",
  "status": "success",
  "timestamp": "2025-11-07T03:00:00Z",
  "result": {
    "tributes": [
      {
        "code": "IMP",
        "description": "Impuesto de Importación",
        "rate": 16.0,
        "base": 10000.00,
        "amount": 1600.00
      },
      {
        "code": "IVA",
        "description": "IVA",
        "rate": 21.0,
        "base": 11600.00,
        "amount": 2436.00
      }
    ],
    "total": 4036.00,
    "validations": [
      {
        "type": "warning",
        "message": "Verificar origen del producto"
      }
    ]
  }
}
```

### 5. Manejo de Errores

**Necesitamos definir:**

- Códigos de error estándar
- Mensajes de error descriptivos
- Estrategia de retry
- Timeout por operación
- Fallback en caso de falla

**Ejemplo de error:**
```json
{
  "operation_id": "DAI-2025-001234",
  "status": "error",
  "error_code": "INVALID_NCM",
  "error_message": "Posición arancelaria no encontrada",
  "details": {
    "ncm_code": "8471.30.99",
    "suggestion": "Verificar código NCM"
  }
}
```

### 6. Validaciones Interactivas

**Preguntas dinámicas del KIT:**

El KIT Malvina puede hacer preguntas adicionales según el tipo de operación:

- ¿Cómo se modelan estas preguntas?
- ¿Cómo se envían las respuestas?
- ¿Hay un flujo de conversación?

**Ejemplo hipotético:**
```json
{
  "operation_id": "DAI-2025-001234",
  "status": "pending_input",
  "questions": [
    {
      "id": "Q1",
      "type": "boolean",
      "text": "¿El producto contiene componentes electrónicos?",
      "required": true
    },
    {
      "id": "Q2",
      "type": "select",
      "text": "Seleccione el tipo de embalaje",
      "options": ["CAJA", "PALLET", "CONTENEDOR"],
      "required": true
    }
  ]
}
```

### 7. Performance y Escalabilidad

**Necesitamos conocer:**

- Tiempo promedio de respuesta del KIT
- Límite de operaciones concurrentes
- Estrategia de balanceo entre Adapters
- Monitoreo de salud de instancias

## Flujo de Trabajo Propuesto

### 1. Validación de Posición Arancelaria

```
Usuario ingresa NCM → Backend valida formato → Envía a RabbitMQ
                                                      ↓
                                              Adapter procesa
                                                      ↓
                                              KIT Malvina valida
                                                      ↓
                                              Adapter envía webhook
                                                      ↓
                                              Backend actualiza operación
                                                      ↓
                                              Frontend muestra resultado
```

### 2. Cálculo de Tributos

```
Usuario completa carátula → Backend valida datos → Envía a RabbitMQ
                                                          ↓
                                                  Adapter calcula
                                                          ↓
                                                  KIT Malvina procesa
                                                          ↓
                                                  Adapter envía webhook
                                                          ↓
                                                  Backend guarda tributos
                                                          ↓
                                                  Frontend muestra liquidación
```

### 3. Validaciones Interactivas

```
KIT requiere datos adicionales → Adapter envía webhook con preguntas
                                            ↓
                                  Backend notifica frontend
                                            ↓
                                  Usuario responde preguntas
                                            ↓
                                  Backend envía respuestas a RabbitMQ
                                            ↓
                                  Adapter continúa procesamiento
```

## Acciones Requeridas

Para completar la integración necesitamos:

1. **Documentación técnica del Adapter**
   - Especificación de mensajes RabbitMQ
   - Especificación de webhooks
   - Ejemplos de requests/responses

2. **Acceso a ambiente de pruebas**
   - Instancia del KIT Malvina de desarrollo
   - Adapter configurado
   - RabbitMQ de testing

3. **Casos de prueba**
   - Operaciones de ejemplo
   - Datos de prueba válidos
   - Escenarios de error

4. **Contacto técnico**
   - Responsable del Adapter
   - Soporte del KIT Malvina
   - Documentación adicional

## Referencias

- Diagrama de arquitectura (util/llm-docs-proyect/graficos.drawio.xml)
- Documento de arquitectura de software (pendiente de revisión)
- Especificación del Adapter .NET (pendiente)

## Estado

🔴 **BLOQUEANTE** - Requiere definición urgente con el equipo de VUCE/DGA para continuar con la implementación del módulo D4.
