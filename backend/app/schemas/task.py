from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import ProjectPriority, ProjectStatus


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: ProjectStatus = ProjectStatus.TODO
    priority: ProjectPriority = ProjectPriority.MEDIUM
    assigned_to: Optional[UUID] = None
    due_datetime: Optional[datetime] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    priority: Optional[ProjectPriority] = None
    assigned_to: Optional[UUID] = None
    due_datetime: Optional[datetime] = None


class TaskResponse(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    description: Optional[str] = None
    status: ProjectStatus
    priority: ProjectPriority
    assigned_to: Optional[UUID] = None
    created_by: UUID
    due_datetime: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
