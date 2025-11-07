from typing import List, Optional

from pydantic import BaseModel, Field


class TaskCreateRequest(BaseModel):
    project: int | str = Field(..., description="ID o slug del proyecto")
    subject: str = Field(..., description="Título de la tarea")
    user_story: Optional[int] = Field(None, description="ID de la historia de usuario")
    description: Optional[str] = Field(None, description="Descripción de la tarea")
    status: Optional[int] = Field(None, description="ID del estado")
    tags: Optional[List[str]] = Field(None, description="Tags de la tarea")


class TaskResponse(BaseModel):
    id: int
    ref: int
    subject: str
    project: int
    user_story: Optional[int] = None
    description: Optional[str] = None
    status: Optional[int] = None
    tags: Optional[List[str]] = None


class UserStoryResponse(BaseModel):
    id: int
    ref: int
    subject: str
    project: int
    description: Optional[str] = None
    status: Optional[int] = None
    tags: Optional[List[str]] = None


class BulkTaskFromMarkdownRequest(BaseModel):
    markdown: str = Field(..., description="Contenido markdown con las tareas")
    project: int | str = Field(..., description="ID o slug del proyecto")
    user_story: int = Field(..., description="ID de la historia de usuario")
    taiga_base_url: Optional[str] = Field(None, description="URL base de Taiga para generar links")


class BulkTaskResponse(BaseModel):
    total_tasks: int
    created_tasks: List[TaskResponse]
    errors: List[dict]
