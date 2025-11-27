# 🚀 Docker Compose: Taiga + Grafana

Solución dockerizada completa para visualizar métricas de Taiga en Grafana.

## Quick Start

```bash
# 1. Configurar variables de entorno
cp .env.docker.example .env.docker
nano .env.docker  # Configurar solo POSTGRES_PASSWORD y GRAFANA_ADMIN_PASSWORD

# 2. Levantar servicios
docker compose up -d

# 3. Configurar token de Taiga desde la interfaz web
# Opción A: Abrir http://localhost:8001/table-map?project=tu-proyecto
#           El modal solicitará el token automáticamente
#
# Opción B: Configurar via API
curl -X POST "http://localhost:8001/auth" \
  -H "Content-Type: application/json" \
  -d '{"token": "tu_token_de_taiga"}'

# 4. Sincronizar datos
curl -X POST "http://localhost:8001/sync?project=tu-proyecto-slug"

# 5. Abrir Grafana
open http://localhost:3003  # Login: admin/admin
```

## Servicios

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| **taiga-app** | 8001 | FastAPI con API de Taiga |
| **grafana** | 3003 | Visualización de métricas |
| **postgres** | 5432 | Base de datos |
| **prometheus** | 9090 | Recolección de métricas |

## Dashboards Disponibles

### 📊 Taiga Metrics Dashboard

- **Velocidad de Sprint**: Story points por sprint
- **Tareas Estancadas**: Alertas de tareas sin movimiento
- **Feed de Actividad**: Timeline de cambios
- **Resumen del Proyecto**: Estadísticas generales

## Configuración

Ver **[docs/grafana-setup.md](./docs/grafana-setup.md)** para:
- Configuración detallada de alertas
- Descripción completa de paneles
- Troubleshooting
- Mantenimiento

## Comandos Útiles

```bash
# Ver logs
docker-compose logs -f taiga-app

# Reiniciar servicio
docker-compose restart taiga-app

# Detener todo
docker-compose down

# Detener y eliminar volúmenes
docker-compose down -v
```

## Estructura de Archivos

```
.
├── docker-compose.yml          # Orquestación de servicios
├── Dockerfile                  # Imagen de taiga-app
├── .env.docker.example         # Template de variables
├── app/
│   └── metrics_exporter.py     # Exportador de métricas
├── grafana/
│   ├── provisioning/
│   │   ├── datasources/        # Configuración de datasources
│   │   └── dashboards/         # Configuración de dashboards
│   └── dashboards/
│       └── taiga-metrics.json  # Dashboard principal
├── prometheus/
│   └── prometheus.yml          # Configuración de Prometheus
└── docs/
    └── grafana-setup.md        # 📖 Documentación completa
```

## Métricas Disponibles

### API Endpoints

- `GET /metrics/sprint-velocity` - Velocidad por sprint
- `GET /metrics/stuck-tasks` - Tareas estancadas
- `GET /metrics/activity-feed` - Actividad reciente
- `GET /metrics/project-summary` - Resumen del proyecto

Ver documentación de API en: http://localhost:8001/docs

## Troubleshooting

**Dashboard vacío?**
```bash
# Ejecutar sincronización
docker-compose exec taiga-app curl -X POST "http://localhost:8001/sync?project=tu-proyecto"
```

**Error de autenticación?**
```bash
# Verificar token
docker-compose exec taiga-app curl "http://localhost:8001/debug/auth"
```

Ver más en **[docs/grafana-setup.md#troubleshooting](./docs/grafana-setup.md#troubleshooting)**
