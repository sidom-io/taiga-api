"""
CRUD operations for database models.

This module provides Create, Read, Update, Delete operations
for all database models.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import DraftBoard, Epic, Project, Tag, Task, TaskTag, UserStory, UserStoryTag


def parse_datetime(value: any) -> datetime:
    """Parse datetime from string or return datetime object."""
    if isinstance(value, str):
        # Parse ISO format datetime from Taiga
        # Remove 'Z' suffix and parse
        if value.endswith('Z'):
            value = value[:-1] + '+00:00'
        return datetime.fromisoformat(value.replace('Z', '+00:00'))
    elif isinstance(value, datetime):
        return value
    else:
        return datetime.utcnow()


# ============================================================================
# PROJECT CRUD
# ============================================================================


async def get_project_by_taiga_id(db: AsyncSession, taiga_id: int) -> Optional[Project]:
    """Get project by Taiga ID."""
    result = await db.execute(select(Project).where(Project.taiga_id == taiga_id))
    return result.scalar_one_or_none()


async def get_project_by_slug(db: AsyncSession, slug: str) -> Optional[Project]:
    """Get project by slug."""
    result = await db.execute(select(Project).where(Project.slug == slug))
    return result.scalar_one_or_none()


async def create_or_update_project(db: AsyncSession, project_data: dict) -> Project:
    """Create or update a project."""
    existing = await get_project_by_taiga_id(db, project_data["id"])

    if existing:
        # Update existing project
        existing.name = project_data["name"]
        existing.slug = project_data["slug"]
        existing.description = project_data.get("description")
        existing.is_private = project_data.get("is_private", False)
        existing.modified_date = parse_datetime(project_data.get("modified_date", datetime.utcnow()))
        existing.raw_data = project_data
        existing.last_synced = datetime.utcnow()
        await db.commit()
        await db.refresh(existing)
        return existing
    else:
        # Create new project
        project = Project(
            taiga_id=project_data["id"],
            name=project_data["name"],
            slug=project_data["slug"],
            description=project_data.get("description"),
            is_private=project_data.get("is_private", False),
            created_date=parse_datetime(project_data.get("created_date", datetime.utcnow())),
            modified_date=parse_datetime(project_data.get("modified_date", datetime.utcnow())),
            raw_data=project_data,
            last_synced=datetime.utcnow(),
        )
        db.add(project)
        await db.commit()
        await db.refresh(project)
        return project


# ============================================================================
# EPIC CRUD
# ============================================================================


async def get_epic_by_taiga_id(db: AsyncSession, taiga_id: int) -> Optional[Epic]:
    """Get epic by Taiga ID."""
    result = await db.execute(select(Epic).where(Epic.taiga_id == taiga_id))
    return result.scalar_one_or_none()


async def list_epics(
    db: AsyncSession, project_id: Optional[int] = None
) -> List[Epic]:
    """List all epics, optionally filtered by project."""
    query = select(Epic)
    if project_id:
        query = query.where(Epic.project_id == project_id)
    result = await db.execute(query.order_by(Epic.ref.desc()))
    return list(result.scalars().all())


async def create_or_update_epic(
    db: AsyncSession, epic_data: dict, project_id: int
) -> Epic:
    """Create or update an epic."""
    existing = await get_epic_by_taiga_id(db, epic_data["id"])

    if existing:
        # Update existing epic
        existing.subject = epic_data["subject"]
        existing.description = epic_data.get("description")
        existing.color = epic_data.get("color")
        existing.ref = epic_data.get("ref")
        existing.modified_date = parse_datetime(epic_data.get("modified_date", datetime.utcnow()))
        existing.raw_data = epic_data
        existing.last_synced = datetime.utcnow()
        await db.commit()
        await db.refresh(existing)
        return existing
    else:
        # Create new epic
        epic = Epic(
            taiga_id=epic_data["id"],
            project_id=project_id,
            ref=epic_data.get("ref"),
            subject=epic_data["subject"],
            description=epic_data.get("description"),
            color=epic_data.get("color"),
            created_date=parse_datetime(epic_data.get("created_date", datetime.utcnow())),
            modified_date=parse_datetime(epic_data.get("modified_date", datetime.utcnow())),
            raw_data=epic_data,
            last_synced=datetime.utcnow(),
        )
        db.add(epic)
        await db.commit()
        await db.refresh(epic)
        return epic


# ============================================================================
# USER STORY CRUD
# ============================================================================


async def get_userstory_by_taiga_id(db: AsyncSession, taiga_id: int) -> Optional[UserStory]:
    """Get user story by Taiga ID."""
    result = await db.execute(
        select(UserStory)
        .where(UserStory.taiga_id == taiga_id)
        .options(selectinload(UserStory.tags))
    )
    return result.scalar_one_or_none()


async def list_userstories(
    db: AsyncSession,
    project_id: Optional[int] = None,
    epic_id: Optional[int] = None,
) -> List[UserStory]:
    """List all user stories, optionally filtered by project or epic."""
    query = select(UserStory).options(selectinload(UserStory.tags))

    if project_id:
        query = query.where(UserStory.project_id == project_id)
    if epic_id:
        query = query.where(UserStory.epic_id == epic_id)

    result = await db.execute(query.order_by(UserStory.ref.desc()))
    return list(result.scalars().all())


async def create_or_update_userstory(
    db: AsyncSession,
    us_data: dict,
    project_id: int,
    epic_id: Optional[int] = None,
) -> UserStory:
    """Create or update a user story."""
    existing = await get_userstory_by_taiga_id(db, us_data["id"])

    if existing:
        # Update existing user story
        existing.epic_id = epic_id
        existing.subject = us_data["subject"]
        existing.description = us_data.get("description")
        existing.status_name = us_data.get("status_extra_info", {}).get("name")
        existing.is_closed = us_data.get("is_closed", False)
        existing.version = us_data.get("version", 1)
        existing.milestone_name = us_data.get("milestone_name")
        existing.ref = us_data.get("ref")
        existing.modified_date = parse_datetime(us_data.get("modified_date", datetime.utcnow()))
        existing.raw_data = us_data
        existing.last_synced = datetime.utcnow()
        await db.commit()
        await db.refresh(existing)
        return existing
    else:
        # Create new user story
        us = UserStory(
            taiga_id=us_data["id"],
            project_id=project_id,
            epic_id=epic_id,
            ref=us_data.get("ref"),
            subject=us_data["subject"],
            description=us_data.get("description"),
            status_name=us_data.get("status_extra_info", {}).get("name"),
            is_closed=us_data.get("is_closed", False),
            version=us_data.get("version", 1),
            milestone_name=us_data.get("milestone_name"),
            created_date=parse_datetime(us_data.get("created_date", datetime.utcnow())),
            modified_date=parse_datetime(us_data.get("modified_date", datetime.utcnow())),
            raw_data=us_data,
            last_synced=datetime.utcnow(),
        )
        db.add(us)
        await db.commit()
        await db.refresh(us)
        return us


# ============================================================================
# TASK CRUD
# ============================================================================


async def get_task_by_taiga_id(db: AsyncSession, taiga_id: int) -> Optional[Task]:
    """Get task by Taiga ID."""
    result = await db.execute(
        select(Task).where(Task.taiga_id == taiga_id).options(selectinload(Task.tags))
    )
    return result.scalar_one_or_none()


async def list_tasks(
    db: AsyncSession,
    project_id: Optional[int] = None,
    userstory_id: Optional[int] = None,
) -> List[Task]:
    """List all tasks, optionally filtered by project or user story."""
    query = select(Task).options(selectinload(Task.tags))

    if project_id:
        query = query.where(Task.project_id == project_id)
    if userstory_id:
        query = query.where(Task.user_story_id == userstory_id)

    result = await db.execute(query.order_by(Task.ref.desc()))
    return list(result.scalars().all())


async def create_or_update_task(
    db: AsyncSession,
    task_data: dict,
    project_id: int,
    userstory_id: Optional[int] = None,
) -> Task:
    """Create or update a task."""
    existing = await get_task_by_taiga_id(db, task_data["id"])

    if existing:
        # Update existing task
        existing.user_story_id = userstory_id
        existing.subject = task_data["subject"]
        existing.description = task_data.get("description")
        existing.status_name = task_data.get("status_extra_info", {}).get("name")
        existing.is_closed = task_data.get("is_closed", False)
        existing.version = task_data.get("version", 1)
        existing.assigned_to_username = task_data.get("assigned_to_extra_info", {}).get("username")
        existing.ref = task_data.get("ref")
        existing.modified_date = parse_datetime(task_data.get("modified_date", datetime.utcnow()))
        existing.raw_data = task_data
        existing.last_synced = datetime.utcnow()
        await db.commit()
        await db.refresh(existing)
        return existing
    else:
        # Create new task
        task = Task(
            taiga_id=task_data["id"],
            project_id=project_id,
            user_story_id=userstory_id,
            ref=task_data.get("ref"),
            subject=task_data["subject"],
            description=task_data.get("description"),
            status_name=task_data.get("status_extra_info", {}).get("name"),
            is_closed=task_data.get("is_closed", False),
            version=task_data.get("version", 1),
            assigned_to_username=task_data.get("assigned_to_extra_info", {}).get("username"),
            created_date=parse_datetime(task_data.get("created_date", datetime.utcnow())),
            modified_date=parse_datetime(task_data.get("modified_date", datetime.utcnow())),
            raw_data=task_data,
            last_synced=datetime.utcnow(),
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        return task


# ============================================================================
# TAG CRUD
# ============================================================================


async def get_or_create_tag(db: AsyncSession, project_id: int, tag_name: str, tag_color: Optional[str] = None) -> Tag:
    """Get existing tag or create new one."""
    result = await db.execute(
        select(Tag).where(Tag.project_id == project_id, Tag.name == tag_name)
    )
    existing = result.scalar_one_or_none()

    if existing:
        # Update color if provided
        if tag_color:
            existing.color = tag_color
            existing.last_synced = datetime.utcnow()
            await db.commit()
            await db.refresh(existing)
        return existing
    else:
        # Create new tag
        tag = Tag(
            project_id=project_id,
            name=tag_name,
            color=tag_color,
            last_synced=datetime.utcnow(),
        )
        db.add(tag)
        await db.commit()
        await db.refresh(tag)
        return tag


async def sync_userstory_tags(
    db: AsyncSession, userstory: UserStory, tag_names: List[str]
) -> None:
    """Sync tags for a user story."""
    # Remove existing tags
    await db.execute(
        select(UserStoryTag).where(UserStoryTag.user_story_id == userstory.id)
    )

    # Add new tags
    for tag_name in tag_names:
        if isinstance(tag_name, list):
            tag_name = tag_name[0] if tag_name else None
        if not tag_name:
            continue

        tag = await get_or_create_tag(db, userstory.project_id, tag_name)

        # Create association
        us_tag = UserStoryTag(user_story_id=userstory.id, tag_id=tag.id)
        db.add(us_tag)

    await db.commit()


async def sync_task_tags(db: AsyncSession, task: Task, tag_names: List[str]) -> None:
    """Sync tags for a task."""
    # Remove existing tags
    await db.execute(select(TaskTag).where(TaskTag.task_id == task.id))

    # Add new tags
    for tag_name in tag_names:
        if isinstance(tag_name, list):
            tag_name = tag_name[0] if tag_name else None
        if not tag_name:
            continue

        tag = await get_or_create_tag(db, task.project_id, tag_name)

        # Create association
        task_tag = TaskTag(task_id=task.id, tag_id=tag.id)
        db.add(task_tag)

    await db.commit()


# ============================================================================
# DRAFT BOARD CRUD
# ============================================================================


async def get_draft_board_state(db: AsyncSession, project_id: int) -> Optional[dict]:
    """Return the stored draft board state for a project."""
    result = await db.execute(select(DraftBoard).where(DraftBoard.project_id == project_id))
    board = result.scalar_one_or_none()
    return board.state if board else None


async def save_draft_board_state(db: AsyncSession, project_id: int, state: dict) -> DraftBoard:
    """Create or update the draft board state for a project."""
    result = await db.execute(select(DraftBoard).where(DraftBoard.project_id == project_id))
    board = result.scalar_one_or_none()

    if board:
        board.state = state
        board.updated_at = datetime.utcnow()
    else:
        board = DraftBoard(project_id=project_id, state=state, updated_at=datetime.utcnow())
        db.add(board)

    await db.commit()
    await db.refresh(board)
    return board
