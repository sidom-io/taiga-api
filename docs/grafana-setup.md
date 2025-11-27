# Grafana + Taiga: Guía de Configuración

Este documento explica cómo usar la integración de Grafana con Taiga FastAPI para visualizar métricas de gestión de proyectos.

## 🚀 Inicio Rápido

### 1. Configuración Inicial

```bash
# 1. Copiar archivo de variables de entorno
cp .env.docker.example .env.docker

# 2. Editar .env.docker y configurar:
# - POSTGRES_PASSWORD: contraseña segura para PostgreSQL
# - GRAFANA_ADMIN_PASSWORD: contraseña de Grafana
# NOTA: El token de Taiga NO se configura aquí, se hace desde la interfaz

nano .env.docker
```

### 2. Levantar Servicios

```bash
# Construir imágenes
docker compose build

# Iniciar todos los servicios
docker compose up -d

# Ver logs
docker compose logs -f taiga-app
```

### 3. Configurar Token de Taiga

El token se configura desde la interfaz web, NO desde variables de entorno:

**Opción A: Interfaz Web (Recomendado)**
1. Abrir http://localhost:8001/table-map?project=tu-proyecto
2. Se mostrará un modal solicitando el token
3. Pegar tu token de Taiga
4. El token se guarda en sesión (memoria del servidor)

**Opción B: API REST**
```bash
curl -X POST "http://localhost:8001/auth" \
  -H "Content-Type: application/json" \
  -d '{"token": "tu_token_de_taiga_aqui"}'
```

**Cómo obtener tu token de Taiga:**
1. Iniciar sesión en Taiga (https://taiga.vuce.gob.ar)
2. Abrir DevTools (F12) → Application/Storage → Cookies
3. Copiar el valor de la cookie `auth-token`

### 4. Verificar Servicios

- **Taiga API**: http://localhost:8001/docs
- **Grafana**: http://localhost:3000
- **Prometheus**: http://localhost:9090

### 4. Primera Sincronización

```bash
# Sincronizar datos de Taiga a la BD local
curl -X POST "http://localhost:8001/sync?project=tu-proyecto-slug" \
  -H "Authorization: Bearer tu_token_aqui"

# O sincronizar todos los proyectos
curl -X POST "http://localhost:8001/sync"
```

## 📊 Dashboard de Grafana

### Acceso

1. Abrir http://localhost:3000
2. Login: `admin` / `admin` (o tu contraseña configurada)
3. Ir a **Dashboards** → **Taiga Metrics Dashboard**

### Paneles Disponibles

#### 1. Velocidad de Sprint
- **Tipo**: Gráfico de líneas (timeseries)
- **Métricas**: Story points completados por sprint
- **Configuración**:
  - Variable `project`: slug del proyecto
  - Últimos 10 sprints por defecto

#### 2. Tareas Estancadas (Gauge)
- **Tipo**: Indicador de nivel
- **Alerta**:
  - 🟢 Verde: < 3 tareas
  - 🟡 Amarillo: 3-5 tareas
  - 🔴 Rojo: > 5 tareas
- **Umbral**: Configurable con variable `days_threshold`

#### 3. Detalle de Tareas Estancadas (Tabla)
- **Columnas**:
  - `#`: Referencia de tarea
  - `Tarea`: Título
  - `Estado`: Estado actual
  - `US`: User Story asociada
  - `Asignado a`: Responsable
  - `Días`: Días sin cambios
  - `Severidad`: Critical / Warning / Info

- **Severidad**:
  - **CRÍTICO** (rojo): > 15 días estancada
  - **ADVERTENCIA** (naranja): > 10 días
  - **INFO** (amarillo): > 5 días

#### 4. Feed de Actividad (Tabla)
- **Eventos**:
  - 🔵 US Creada
  - 🟦 US Actualizada
  - 🟢 Tarea Creada
  - 🟩 Tarea Actualizada

- **Filtros**:
  - `activity_hours`: horas atrás (168 = 1 semana)
  - `activity_limit`: máximo de eventos (50)

#### 5. Resumen del Proyecto
- **Métricas**:
  - Total de tareas
  - % de completado (gauge)
  - Total de user stories
  - Total de épicas

### Variables del Dashboard

Configurables en la parte superior:

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `project` | Slug del proyecto | `vuce-sidom-dai` |
| `days_threshold` | Días para tarea estancada | `5` |
| `activity_limit` | Eventos en feed | `50` |
| `activity_hours` | Horas de actividad | `168` (1 semana) |

## 🔔 Configuración de Alertas

### Crear Alerta de Tareas Estancadas

1. En el panel "Tareas Estancadas (Gauge)", click en el título → **Edit**
2. Ir a la pestaña **Alert**
3. **Create alert rule from this panel**
4. Configurar:
   - **Condition**: `WHEN count() OF query(A) IS ABOVE 5`
   - **Evaluate**: every `5m` for `10m`
   - **Notification**: elegir canal (Email, Slack, etc.)

### Canales de Notificación

#### Email

1. **Alerting** → **Contact points** → **New contact point**
2. **Name**: `Email Alerts`
3. **Type**: `Email`
4. **Addresses**: `tu-email@ejemplo.com`
5. **Save**

#### Slack

1. Crear Slack webhook: https://api.slack.com/messaging/webhooks
2. **Contact points** → **New contact point**
3. **Type**: `Slack`
4. **Webhook URL**: pegar URL
5. **Save**

## 📈 Endpoints de Métricas

### Sprint Velocity

```bash
GET /metrics/sprint-velocity?project=<slug>&sprint_count=6&use_milestones=false
```

**Respuesta**:
```json
{
  "project_id": 3,
  "project_name": "VUCE SIDOM DAI",
  "sprint_count": 6,
  "sprints": [
    {
      "sprint_id": "2025-W03",
      "tasks_completed": 15,
      "story_points": 42.0
    }
  ]
}
```

### Stuck Tasks

```bash
GET /metrics/stuck-tasks?project=<slug>&days_threshold=5
```

**Respuesta**:
```json
{
  "total_stuck": 3,
  "by_severity": {
    "critical": 1,
    "warning": 2,
    "info": 0
  },
  "tasks": [
    {
      "ref": 150,
      "subject": "Implementar API de permisos",
      "status": "In Progress",
      "days_stuck": 12,
      "severity": "warning",
      "assigned_to": "Juan Pérez"
    }
  ]
}
```

### Activity Feed

```bash
GET /metrics/activity-feed?project=<slug>&limit=50&hours=168
```

### Project Summary

```bash
GET /metrics/project-summary?project=<slug>
```

## 🔧 Mantenimiento

### Actualizar Datos

El dashboard se actualiza automáticamente cada 30 segundos, pero los datos vienen de la BD local que se sincroniza manualmente:

```bash
# Sincronización manual
curl -X POST "http://localhost:8001/sync?project=tu-proyecto"

# Programar sincronización automática (crontab)
*/30 * * * * curl -X POST "http://localhost:8001/sync?project=tu-proyecto"
```

### Ver Logs

```bash
# Logs de Taiga app
docker-compose logs -f taiga-app

# Logs de Grafana
docker-compose logs -f grafana

# Logs de todos los servicios
docker-compose logs -f
```

### Reiniciar Servicios

```bash
# Reiniciar todo
docker-compose restart

# Reiniciar servicio específico
docker-compose restart taiga-app
docker-compose restart grafana
```

### Backup de Datos

```bash
# Backup de PostgreSQL
docker-compose exec postgres pg_dump -U taiga taiga_db > backup_$(date +%Y%m%d).sql

# Backup de Grafana dashboards (se persisten en volumen)
docker-compose exec grafana tar czf - /var/lib/grafana/dashboards > grafana_backup.tar.gz
```

## 🐛 Troubleshooting

### Problema: Dashboard muestra "No Data"

**Causa**: No hay datos sincronizados en la BD local

**Solución**:
```bash
# 1. Verificar que taiga-app esté corriendo
docker-compose ps

# 2. Ejecutar sincronización
curl -X POST "http://localhost:8001/sync?project=tu-proyecto"

# 3. Verificar en logs
docker-compose logs taiga-app | grep sync
```

### Problema: Error de autenticación

**Causa**: Token de Taiga inválido o expirado

**Solución**:
```bash
# 1. Actualizar token en .env.docker
nano .env.docker

# 2. Reiniciar servicio
docker-compose restart taiga-app

# 3. Verificar autenticación
curl http://localhost:8001/debug/auth
```

### Problema: Grafana no conecta a PostgreSQL

**Causa**: Credenciales incorrectas o servicio no saludable

**Solución**:
```bash
# 1. Verificar que postgres esté healthy
docker-compose ps postgres

# 2. Verificar credenciales en .env.docker

# 3. Reiniciar servicios
docker-compose restart postgres grafana
```

### Problema: Métricas de sprint vacías

**Causa**: No hay milestones configurados en Taiga o tareas sin fechas

**Solución**:
- Opción 1: Crear milestones en Taiga y asociar user stories
- Opción 2: Usar modo semanal: `use_milestones=false`

## 📚 Recursos Adicionales

- **API Docs**: http://localhost:8001/docs
- **Grafana Docs**: https://grafana.com/docs/
- **Prometheus Docs**: https://prometheus.io/docs/
- **Taiga API**: https://docs.taiga.io/api.html

## 🎯 Mejoras Futuras

- [ ] Webhooks de Taiga para sincronización en tiempo real
- [ ] Burndown charts por sprint
- [ ] Métricas de cycle time y lead time
- [ ] Predicción de velocidad con ML
- [ ] Exportador de Prometheus nativo
- [ ] Dashboard de rendimiento individual
