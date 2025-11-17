"""
Synchronization service for Taiga data.

This module handles syncing data from Taiga API to local database.
"""

from typing import Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from app import crud
from app.taiga_client import TaigaClient


class SyncStats:
    """Statistics for sync operations."""

    def __init__(self) -> None:
        self.projects_created = 0
        self.projects_updated = 0
        self.epics_created = 0
        self.epics_updated = 0
        self.userstories_created = 0
        self.userstories_updated = 0
        self.tasks_created = 0
        self.tasks_updated = 0
        self.tags_created = 0
        self.errors: List[str] = []

    def to_dict(self) -> Dict[str, any]:
        """Convert stats to dictionary."""
        return {
            "projects": {
                "created": self.projects_created,
                "updated": self.projects_updated,
                "total": self.projects_created + self.projects_updated,
            },
            "epics": {
                "created": self.epics_created,
                "updated": self.epics_updated,
                "total": self.epics_created + self.epics_updated,
            },
            "user_stories": {
                "created": self.userstories_created,
                "updated": self.userstories_updated,
                "total": self.userstories_created + self.userstories_updated,
            },
            "tasks": {
                "created": self.tasks_created,
                "updated": self.tasks_updated,
                "total": self.tasks_created + self.tasks_updated,
            },
            "tags": {"created": self.tags_created},
            "errors": self.errors,
            "success": len(self.errors) == 0,
        }


async def sync_project(
    db: AsyncSession,
    taiga_client: TaigaClient,
    project_id_or_slug: int | str,
    stats: SyncStats,
) -> None:
    """
    Sync a single project from Taiga to local database.

    This syncs:
    - Project metadata
    - All epics in the project
    - All user stories (with their epic associations)
    - All tasks (with their user story associations)
    - All tags

    Args:
        db: Database session
        taiga_client: Taiga API client
        project_id_or_slug: Project ID or slug
        stats: Sync statistics tracker
    """
    try:
        # 1. Get and sync project
        project_data = await taiga_client.get_project(project_id_or_slug)
        existing_project = await crud.get_project_by_taiga_id(db, project_data["id"])

        project = await crud.create_or_update_project(db, project_data)

        if existing_project:
            stats.projects_updated += 1
        else:
            stats.projects_created += 1

        project_db_id = project.id
        project_taiga_id = project.taiga_id

        # 2. Sync epics
        epics_data = await taiga_client.list_epics(project_taiga_id)

        for epic_data in epics_data:
            try:
                # Get full epic details (including description)
                full_epic_data = await taiga_client.get_epic(epic_data["id"])

                existing_epic = await crud.get_epic_by_taiga_id(db, full_epic_data["id"])
                await crud.create_or_update_epic(db, full_epic_data, project_db_id)

                if existing_epic:
                    stats.epics_updated += 1
                else:
                    stats.epics_created += 1
            except Exception as e:
                stats.errors.append(f"Error syncing epic {epic_data.get('id')}: {str(e)}")

        # 3. Sync user stories
        userstories_data = await taiga_client.list_user_stories(
            project_taiga_id, titles_only=False
        )

        # Create epic_id mapping (taiga_id -> db_id)
        epic_mapping = {}
        for epic_data in epics_data:
            epic = await crud.get_epic_by_taiga_id(db, epic_data["id"])
            if epic:
                epic_mapping[epic_data["id"]] = epic.id

        for us_data in userstories_data:
            try:
                # Get full user story details (including description)
                full_us_data = await taiga_client.get_user_story(us_data["id"])
                
                # Get epic DB ID if user story belongs to an epic
                # Note: Taiga API returns 'epics' as array, use first epic if exists
                epic_db_id = None
                epic_taiga_id = full_us_data.get("epic")  # Try singular first (some endpoints)
                if not epic_taiga_id and full_us_data.get("epics"):  # Try plural (array)
                    # Get first epic from array
                    epics_list = full_us_data.get("epics", [])
                    if epics_list and len(epics_list) > 0:
                        epic_taiga_id = epics_list[0].get("id")

                if epic_taiga_id:
                    epic_db_id = epic_mapping.get(epic_taiga_id)

                existing_us = await crud.get_userstory_by_taiga_id(db, full_us_data["id"])
                us = await crud.create_or_update_userstory(
                    db, full_us_data, project_db_id, epic_db_id
                )

                # Sync tags for user story
                if full_us_data.get("tags"):
                    await crud.sync_userstory_tags(db, us, full_us_data["tags"])

                if existing_us:
                    stats.userstories_updated += 1
                else:
                    stats.userstories_created += 1
            except Exception as e:
                stats.errors.append(
                    f"Error syncing user story {us_data.get('id')}: {str(e)}"
                )

        # 4. Sync tasks
        tasks_data = await taiga_client.list_tasks(project_taiga_id)

        # Create user story mapping (taiga_id -> db_id)
        us_mapping = {}
        for us_data in userstories_data:
            us = await crud.get_userstory_by_taiga_id(db, us_data["id"])
            if us:
                us_mapping[us_data["id"]] = us.id

        for task_data in tasks_data:
            try:
                # Get full task details (including description)
                full_task_data = await taiga_client.get_task(task_data["id"])

                # Get user story DB ID if task belongs to one
                us_db_id = None
                if full_task_data.get("user_story"):
                    us_db_id = us_mapping.get(full_task_data["user_story"])

                existing_task = await crud.get_task_by_taiga_id(db, full_task_data["id"])
                task = await crud.create_or_update_task(
                    db, full_task_data, project_db_id, us_db_id
                )

                # Sync tags for task
                if full_task_data.get("tags"):
                    await crud.sync_task_tags(db, task, full_task_data["tags"])

                if existing_task:
                    stats.tasks_updated += 1
                else:
                    stats.tasks_created += 1
            except Exception as e:
                stats.errors.append(f"Error syncing task {task_data.get('id')}: {str(e)}")

    except Exception as e:
        stats.errors.append(f"Error syncing project {project_id_or_slug}: {str(e)}")


async def sync_all_projects(
    db: AsyncSession, taiga_client: TaigaClient
) -> SyncStats:
    """
    Sync all accessible projects from Taiga.

    Args:
        db: Database session
        taiga_client: Taiga API client

    Returns:
        Sync statistics
    """
    stats = SyncStats()

    try:
        projects = await taiga_client.list_projects()

        for project_data in projects:
            await sync_project(db, taiga_client, project_data["id"], stats)

    except Exception as e:
        stats.errors.append(f"Error listing projects: {str(e)}")

    return stats
