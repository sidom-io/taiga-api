"""
Metrics Exporter for Taiga - Grafana Integration

Este módulo extrae métricas de la base de datos local de Taiga
para visualización en Grafana.

Métricas incluidas:
- Velocidad de sprint (story points completados)
- Tareas estancadas (en progreso > X días)
- Timeline de actividad y comentarios
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Epic, Project, Task, UserStory


class MetricsExporter:
    """Exportador de métricas de Taiga para Grafana"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_sprint_velocity(
        self,
        project_id: int,
        sprint_count: int = 6,
    ) -> List[Dict]:
        """
        Calcula la velocidad de sprint basada en tareas completadas.

        Args:
            project_id: ID del proyecto
            sprint_count: Número de sprints a incluir (últimos N)

        Returns:
            Lista de métricas por sprint con story points y tareas completadas
        """
        # Por ahora, calculamos velocidad basada en fechas de modificación
        # En el futuro, esto debería usar milestones/sprints de Taiga

        # Get user stories grouped by milestone (sprint)
        # Mostramos todos los puntos asignados al sprint, independientemente de si están cerrados
        query = select(
            UserStory.milestone_name.label("sprint_week"),
            func.count(UserStory.id).label("tasks_completed"),
            func.coalesce(func.sum(UserStory.total_points), 0).label("story_points"),
        ).where(
            and_(
                UserStory.project_id == project_id,
                UserStory.milestone_name.isnot(None),
            )
        ).group_by(UserStory.milestone_name).order_by(UserStory.milestone_name)

        result = await self.db.execute(query)
        rows = result.all()

        metrics = []
        for row in rows:
            sprint_name = row.sprint_week
            metrics.append({
                "sprint_start": None, # No tenemos fecha de inicio fácil aquí
                "tasks_completed": row.tasks_completed or 0,
                "story_points": float(row.story_points or 0),
                "sprint_id": sprint_name,
            })

        return metrics

    async def get_sprint_velocity_by_milestone(
        self,
        project_id: int,
        limit: int = 6,
    ) -> List[Dict]:
        """
        Calcula velocidad de sprint basada en milestones de Taiga.

        Requiere que raw_data de UserStory contenga información de milestone.
        """
        # Consultar user stories con milestones
        query = select(
            UserStory.raw_data["milestone"].label("milestone_id"),
            UserStory.raw_data["milestone_name"].label("milestone_name"),
            func.count(UserStory.id).label("stories_count"),
            func.coalesce(func.sum(UserStory.total_points), 0).label("story_points"),
        ).where(
            and_(
                UserStory.project_id == project_id,
                UserStory.raw_data["milestone"].isnot(None),
                UserStory.is_closed.is_(True),
            )
        ).group_by(
            UserStory.raw_data["milestone"],
            UserStory.raw_data["milestone_name"],
        ).order_by(
            UserStory.raw_data["milestone"].desc()
        ).limit(limit)

        result = await self.db.execute(query)
        rows = result.all()

        metrics = []
        for row in rows:
            metrics.append({
                "milestone_id": row.milestone_id,
                "milestone_name": row.milestone_name or f"Milestone {row.milestone_id}",
                "stories_completed": row.stories_count or 0,
                "story_points": float(row.story_points or 0),
            })

        return metrics

    async def get_stuck_tasks(
        self,
        project_id: int,
        days_threshold: int = 5,
        exclude_statuses: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Detecta tareas estancadas en estados intermedios.

        Args:
            project_id: ID del proyecto
            days_threshold: Días mínimos sin cambios para considerar estancada
            exclude_statuses: Estados a excluir (ej: ["Done", "Closed"])

        Returns:
            Lista de tareas estancadas con información relevante
        """
        if exclude_statuses is None:
            exclude_statuses = ["Done", "Closed", "Ready for test"]

        # Calcular fecha límite
        threshold_date = datetime.now() - timedelta(days=days_threshold)

        # Buscar tareas no cerradas y sin modificaciones recientes
        query = select(Task).options(selectinload(Task.user_story)).where(
            and_(
                Task.project_id == project_id,
                Task.is_closed.is_(False),
                or_(
                    Task.modified_date < threshold_date,
                    Task.modified_date.is_(None),
                ),
            )
        ).order_by(Task.modified_date.asc())

        result = await self.db.execute(query)
        tasks = result.scalars().all()

        stuck_tasks = []
        for task in tasks:
            # Obtener estado desde raw_data
            raw_data = task.raw_data or {}
            status_name = raw_data.get("status_extra_info", {}).get("name", "Unknown")

            # Excluir estados finales
            if any(excl.lower() in status_name.lower() for excl in exclude_statuses):
                continue

            # Calcular días estancada
            modified = task.modified_date or task.created_date
            days_stuck = (datetime.now() - modified).days if modified else 999

            stuck_tasks.append({
                "task_id": task.id,
                "taiga_id": task.taiga_id,
                "ref": task.ref,
                "subject": task.subject,
                "status": status_name,
                "user_story_ref": task.user_story.ref if task.user_story else None,
                "user_story_subject": task.user_story.subject if task.user_story else None,
                "assigned_to": raw_data.get("assigned_to_extra_info", {}).get("full_name_display"),
                "days_stuck": days_stuck,
                "last_modified": modified.isoformat() if modified else None,
                "severity": self._calculate_severity(days_stuck, days_threshold),
            })

        return stuck_tasks

    async def get_activity_feed(
        self,
        project_id: int,
        limit: int = 50,
        hours: int = 168,  # 1 semana por defecto
    ) -> List[Dict]:
        """
        Obtiene feed de actividad: creación, modificación y comentarios.

        Args:
            project_id: ID del proyecto
            limit: Número máximo de eventos
            hours: Horas atrás para buscar actividad

        Returns:
            Lista de eventos de actividad ordenados por fecha
        """
        cutoff_date = datetime.now() - timedelta(hours=hours)

        # Actividad de user stories
        us_query = select(
            UserStory.id,
            UserStory.ref,
            UserStory.subject,
            UserStory.modified_date,
            UserStory.created_date,
            UserStory.raw_data,
        ).where(
            and_(
                UserStory.project_id == project_id,
                or_(
                    UserStory.modified_date >= cutoff_date,
                    UserStory.created_date >= cutoff_date,
                ),
            )
        ).order_by(UserStory.modified_date.desc())

        us_result = await self.db.execute(us_query)
        user_stories = us_result.all()

        # Actividad de tareas
        task_query = select(
            Task.id,
            Task.ref,
            Task.subject,
            Task.modified_date,
            Task.created_date,
            Task.raw_data,
            Task.user_story_id,
        ).where(
            and_(
                Task.project_id == project_id,
                or_(
                    Task.modified_date >= cutoff_date,
                    Task.created_date >= cutoff_date,
                ),
            )
        ).order_by(Task.modified_date.desc())

        task_result = await self.db.execute(task_query)
        tasks = task_result.all()

        # Combinar y formatear actividad
        activities = []

        for us in user_stories:
            raw_data = us.raw_data or {}

            # Evento de creación
            if us.created_date >= cutoff_date:
                activities.append({
                    "timestamp": us.created_date.isoformat(),
                    "type": "user_story_created",
                    "ref": us.ref,
                    "subject": us.subject,
                    "description": f"User Story #{us.ref} created",
                    "author": raw_data.get("owner_extra_info", {}).get("full_name_display"),
                })

            # Evento de modificación
            if us.modified_date and us.modified_date >= cutoff_date and us.modified_date != us.created_date:
                activities.append({
                    "timestamp": us.modified_date.isoformat(),
                    "type": "user_story_updated",
                    "ref": us.ref,
                    "subject": us.subject,
                    "description": f"User Story #{us.ref} updated",
                    "author": raw_data.get("modified_by_extra_info", {}).get("full_name_display"),
                })

        for task in tasks:
            raw_data = task.raw_data or {}

            # Evento de creación
            if task.created_date >= cutoff_date:
                activities.append({
                    "timestamp": task.created_date.isoformat(),
                    "type": "task_created",
                    "ref": task.ref,
                    "subject": task.subject,
                    "description": f"Task #{task.ref} created",
                    "author": raw_data.get("owner_extra_info", {}).get("full_name_display"),
                })

            # Evento de modificación
            if task.modified_date and task.modified_date >= cutoff_date and task.modified_date != task.created_date:
                activities.append({
                    "timestamp": task.modified_date.isoformat(),
                    "type": "task_updated",
                    "ref": task.ref,
                    "subject": task.subject,
                    "description": f"Task #{task.ref} updated",
                    "author": raw_data.get("modified_by_extra_info", {}).get("full_name_display"),
                    "status": raw_data.get("status_extra_info", {}).get("name"),
                })

        # Ordenar por timestamp descendente y limitar
        activities.sort(key=lambda x: x["timestamp"], reverse=True)
        return activities[:limit]

    def _calculate_severity(self, days_stuck: int, threshold: int) -> str:
        """
        Calcula severidad de tarea estancada.

        Returns:
            "critical", "warning", o "info"
        """
        if days_stuck >= threshold * 3:
            return "critical"
        elif days_stuck >= threshold * 2:
            return "warning"
        else:
            return "info"

    async def get_project_summary(self, project_id: int) -> Dict:
        """
        Obtiene resumen general del proyecto para Grafana.

        Returns:
            Diccionario con conteos y estadísticas del proyecto
        """
        # Total de épicas
        epic_count = await self.db.scalar(
            select(func.count(Epic.id)).where(Epic.project_id == project_id)
        )

        # Total de user stories
        us_count = await self.db.scalar(
            select(func.count(UserStory.id)).where(UserStory.project_id == project_id)
        )

        # Total de tareas
        task_count = await self.db.scalar(
            select(func.count(Task.id)).where(Task.project_id == project_id)
        )

        # Tareas completadas
        tasks_done = await self.db.scalar(
            select(func.count(Task.id)).where(
                and_(
                    Task.project_id == project_id,
                    Task.is_closed.is_(True),
                )
            )
        )

        # User stories completadas
        us_done = await self.db.scalar(
            select(func.count(UserStory.id)).where(
                and_(
                    UserStory.project_id == project_id,
                    UserStory.is_closed.is_(True),
                )
            )
        )

        return {
            "project_id": project_id,
            "epics": epic_count or 0,
            "user_stories": {
                "total": us_count or 0,
                "completed": us_done or 0,
                "in_progress": (us_count or 0) - (us_done or 0),
            },
            "tasks": {
                "total": task_count or 0,
                "completed": tasks_done or 0,
                "in_progress": (task_count or 0) - (tasks_done or 0),
            },
            "completion_rate": {
                "tasks": round((tasks_done or 0) / (task_count or 1) * 100, 2),
                "user_stories": round((us_done or 0) / (us_count or 1) * 100, 2),
            },
        }
