from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.enums import Role


class ProjectMemberCreate(BaseModel):
    user_id: UUID
    role: Role = Role.USER


class ProjectMemberUpdate(BaseModel):
    role: Role


class ProjectMemberResponse(BaseModel):
    id: UUID
    user_id: UUID
    project_id: UUID
    role: Role
    created_at: datetime
