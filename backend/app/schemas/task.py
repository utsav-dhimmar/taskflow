from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.db.models.enums import ProjectPriority, ProjectStatus


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    status: ProjectStatus = ProjectStatus.TODO
    priority: ProjectPriority = ProjectPriority.MEDIUM
    assigned_to: UUID | None = None
    due_datetime: datetime | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    status: ProjectStatus | None = None
    priority: ProjectPriority | None = None
    assigned_to: UUID | None = None
    due_datetime: datetime | None = None


class TaskResponse(BaseModel):
    id: UUID
    project_id: UUID
    title: str
    description: str | None = None
    status: ProjectStatus
    priority: ProjectPriority
    assigned_to: UUID | None = None
    created_by: UUID
    due_datetime: datetime | None = None
    created_at: datetime
    updated_at: datetime
