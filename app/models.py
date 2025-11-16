"""
SQLAlchemy models for Taiga entities.

These models represent the local synchronized copy of Taiga data.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Project(Base):
    """Project model - represents a Taiga project."""

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    taiga_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_private: Mapped[bool] = mapped_column(default=False)
    created_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    modified_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Raw JSON data from Taiga API
    raw_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Sync metadata
    last_synced: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    epics: Mapped[List["Epic"]] = relationship("Epic", back_populates="project", cascade="all, delete-orphan")
    user_stories: Mapped[List["UserStory"]] = relationship("UserStory", back_populates="project", cascade="all, delete-orphan")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="project", cascade="all, delete-orphan")
    tags: Mapped[List["Tag"]] = relationship("Tag", back_populates="project", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, taiga_id={self.taiga_id}, name='{self.name}')>"


class Epic(Base):
    """Epic model - high-level feature grouping."""

    __tablename__ = "epics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    taiga_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    ref: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Timestamps
    created_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    modified_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Raw JSON data from Taiga API
    raw_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Sync metadata
    last_synced: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="epics")
    user_stories: Mapped[List["UserStory"]] = relationship("UserStory", back_populates="epic")

    def __repr__(self) -> str:
        return f"<Epic(id={self.id}, taiga_id={self.taiga_id}, subject='{self.subject}')>"


class UserStory(Base):
    """User Story model - user-facing feature."""

    __tablename__ = "user_stories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    taiga_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    epic_id: Mapped[Optional[int]] = mapped_column(ForeignKey("epics.id"), nullable=True)
    ref: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Taiga metadata
    is_closed: Mapped[bool] = mapped_column(default=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    milestone_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Timestamps
    created_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    modified_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Raw JSON data from Taiga API
    raw_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Sync metadata
    last_synced: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="user_stories")
    epic: Mapped[Optional["Epic"]] = relationship("Epic", back_populates="user_stories")
    tasks: Mapped[List["Task"]] = relationship("Task", back_populates="user_story", cascade="all, delete-orphan")
    tags: Mapped[List["UserStoryTag"]] = relationship("UserStoryTag", back_populates="user_story", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<UserStory(id={self.id}, taiga_id={self.taiga_id}, subject='{self.subject}')>"


class Task(Base):
    """Task model - smallest unit of work."""

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    taiga_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    user_story_id: Mapped[Optional[int]] = mapped_column(ForeignKey("user_stories.id"), nullable=True)
    ref: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Taiga metadata
    is_closed: Mapped[bool] = mapped_column(default=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    assigned_to_username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Timestamps
    created_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    modified_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # Raw JSON data from Taiga API
    raw_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Sync metadata
    last_synced: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="tasks")
    user_story: Mapped[Optional["UserStory"]] = relationship("UserStory", back_populates="tasks")
    tags: Mapped[List["TaskTag"]] = relationship("TaskTag", back_populates="task", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Task(id={self.id}, taiga_id={self.taiga_id}, subject='{self.subject}')>"


class Tag(Base):
    """Tag model - labels for categorization."""

    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    color: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Sync metadata
    last_synced: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="tags")
    user_story_tags: Mapped[List["UserStoryTag"]] = relationship("UserStoryTag", back_populates="tag", cascade="all, delete-orphan")
    task_tags: Mapped[List["TaskTag"]] = relationship("TaskTag", back_populates="tag", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Tag(id={self.id}, name='{self.name}', color='{self.color}')>"


class UserStoryTag(Base):
    """Association table for User Stories and Tags (many-to-many)."""

    __tablename__ = "user_story_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_story_id: Mapped[int] = mapped_column(ForeignKey("user_stories.id"), nullable=False)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), nullable=False)

    # Relationships
    user_story: Mapped["UserStory"] = relationship("UserStory", back_populates="tags")
    tag: Mapped["Tag"] = relationship("Tag", back_populates="user_story_tags")

    def __repr__(self) -> str:
        return f"<UserStoryTag(user_story_id={self.user_story_id}, tag_id={self.tag_id})>"


class TaskTag(Base):
    """Association table for Tasks and Tags (many-to-many)."""

    __tablename__ = "task_tags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id"), nullable=False)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), nullable=False)

    # Relationships
    task: Mapped["Task"] = relationship("Task", back_populates="tags")
    tag: Mapped["Tag"] = relationship("Tag", back_populates="task_tags")

    def __repr__(self) -> str:
        return f"<TaskTag(task_id={self.task_id}, tag_id={self.tag_id})>"
