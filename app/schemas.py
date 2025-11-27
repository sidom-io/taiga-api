from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class TaskCreateRequest(BaseModel):
    project: int | str = Field(..., description="ID o slug del proyecto")
    subject: str = Field(..., description="Título de la tarea")
    user_story: Optional[int] = Field(None, description="ID de la historia de usuario")
    description: Optional[str] = Field(None, description="Descripción de la tarea")
    status: Optional[int] = Field(None, description="ID del estado")
    tags: Optional[List[str]] = Field(None, description="Tags de la tarea")


class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="allow")  # Permitir campos adicionales de Taiga

    id: int
    ref: int
    subject: str
    project: int
    user_story: Optional[int] = None
    description: Optional[str] = None
    status: Optional[int] = None
    tags: Optional[List[Any]] = None

    @field_validator("tags", mode="before")
    @classmethod
    def flatten_tags(cls, v):
        """Normaliza tags que vienen como lista de listas desde Taiga."""
        if v is None:
            return None
        if isinstance(v, list):
            # Aplanar lista de listas y filtrar None
            flattened = []
            for item in v:
                if isinstance(item, list):
                    flattened.extend([x for x in item if x is not None])
                elif item is not None:
                    flattened.append(item)
            return flattened
        return v


class UserStoryResponse(BaseModel):
    model_config = ConfigDict(extra="allow")  # Permitir campos adicionales de Taiga

    id: int
    ref: int
    subject: str
    project: int
    epic: Optional[int] = None
    backlog_order: Optional[int] = None
    description: Optional[str] = None
    status: Optional[int] = None
    tags: Optional[List[Any]] = None

    @field_validator("tags", mode="before")
    @classmethod
    def flatten_tags(cls, v):
        """Normaliza tags que vienen como lista de listas desde Taiga."""
        if v is None:
            return None
        if isinstance(v, list):
            # Aplanar lista de listas y filtrar None
            flattened = []
            for item in v:
                if isinstance(item, list):
                    flattened.extend([x for x in item if x is not None])
                elif item is not None:
                    flattened.append(item)
            return flattened
        return v


class UserStoryDetailResponse(UserStoryResponse):
    """Schema para user story con tareas incluidas"""

    tasks: Optional[List["TaskResponse"]] = None
    total_tasks: int = 0


class BulkTaskFromMarkdownRequest(BaseModel):
    markdown: str = Field(..., description="Contenido markdown con las tareas")
    project: int | str = Field(..., description="ID o slug del proyecto")
    user_story: int = Field(..., description="ID de la historia de usuario")
    taiga_base_url: Optional[str] = Field(None, description="URL base de Taiga para generar links")


class BulkTaskResponse(BaseModel):
    total_tasks: int
    created_tasks: List[TaskResponse]
    errors: List[dict]


# Epic schemas
class EpicResponse(BaseModel):
    """Schema base para épicas con campos esenciales"""

    id: int
    ref: int
    subject: str
    project: int
    color: Optional[str] = None
    description: Optional[str] = None
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None


class EpicDetailResponse(EpicResponse):
    """Schema para épica con relaciones (user stories y tareas)"""

    user_stories: Optional[List[UserStoryResponse]] = None
    total_user_stories: int = 0
    tasks: Optional[List[TaskResponse]] = None
    total_tasks: int = 0


# Authentication schemas
class TokenSetRequest(BaseModel):
    """Request para establecer un bearer token manualmente"""

    token: str = Field(..., description="Bearer token obtenido de Taiga")


class AuthStatusResponse(BaseModel):
    """Response del estado de autenticación actual"""

    authenticated: bool
    user: Optional[str] = None
    token_preview: Optional[str] = None
    expires_at: Optional[datetime] = None
    error: Optional[str] = None
    message: Optional[str] = None


class DraftStatePayload(BaseModel):
    """Payload para persistir el estado del borrador."""

    state: dict
