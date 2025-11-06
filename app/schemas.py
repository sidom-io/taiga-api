from typing import Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class TaskCreateRequest(BaseModel):
    project: Union[int, str] = Field(..., description="ID numérico o slug del proyecto")
    subject: str = Field(..., min_length=1, description="Título de la tarea")
    user_story: Optional[int] = Field(
        default=None, description="ID de la user story asociada (opcional)"
    )
    description: Optional[str] = Field(
        default=None, description="Descripción de la tarea (opcional)"
    )


class TaskResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    subject: str
    project: Optional[int] = None
    user_story: Optional[int] = None
    ref: Optional[int] = None


class UserStoryResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: int
    subject: str
    project: Optional[int] = None
    ref: Optional[int] = None
    description: Optional[str] = None
