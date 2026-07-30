from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ProjectCreate(BaseModel):
    name: str
    description: str | None = None


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None


class ProjectResponse(BaseModel):
    id: UUID
    name: str
    description: str | None = None
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
