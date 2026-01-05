from datetime import datetime
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel
from app.models.enums import Role


class Project(SQLModel, table=True):
    __tablename__ = "projects"
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    name: str
    description: str | None = Field(default=None)
    owner_id: UUID = Field(foreign_key="users.id", ondelete="CASCADE")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ProjectMember(SQLModel, table=True):
    __tablename__ = "project_members"
    id: UUID = Field(default_factory=uuid4, primary_key=True, index=True)
    user_id: UUID = Field(foreign_key="users.id", ondelete="CASCADE")
    project_id: UUID = Field(foreign_key="projects.id", ondelete="CASCADE")
    role: Role = Field(default=Role.USER)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
