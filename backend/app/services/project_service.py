from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.main import get_session
from app.db.models.enums import Role
from app.db.models.project import Project, ProjectMember
from app.db.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_project(
        self, project_create: ProjectCreate, user: User
    ) -> Project:
        """
        Create a new project
        """
        # project creator aka admin is project owner
        db_project = Project(
            name=project_create.name,
            description=project_create.description,
            owner_id=user.id,
        )
        self.session.add(db_project)
        await self.session.commit()
        await self.session.refresh(db_project)

        # project creator aka admin is also member
        member = ProjectMember(
            user_id=user.id, project_id=db_project.id, role=Role.ADMIN
        )
        self.session.add(member)
        await self.session.commit()

        return db_project

    async def get_projects_for_user(self, user: User) -> Sequence[Project]:
        # Get all Projects where user is member or owner
        statement = (
            select(Project)
            .join(
                ProjectMember,
                Project.id == ProjectMember.project_id,
                isouter=True,
            )
            .join(
                User,
                ProjectMember.user_id == User.id,
                isouter=True,
            )
            .where(
                or_(
                    Project.owner_id == user.id,
                    ProjectMember.user_id == user.id,
                )
            )
            .distinct()
        )

        result = await self.session.execute(statement)
        return result.scalars().all()

    async def get_project_by_id(
        self, project_id: UUID, user: User
    ) -> Project | None:
        project = await self.session.get(Project, project_id)
        if not project:
            return None

        if project.owner_id == user.id:
            return project

        statement = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user.id,
        )
        member = (await self.session.execute(statement)).scalars().first()
        if member:
            return project

        return None

    async def get_project_members(
        self, project_id: UUID
    ) -> Sequence[ProjectMember]:
        statement = select(ProjectMember).where(
            ProjectMember.project_id == project_id
        )
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def add_project_member(
        self, project_id: UUID, user_id: UUID, role: Role
    ) -> ProjectMember:
        statement = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        existing = (await self.session.execute(statement)).scalars().first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this project",
            )

        member = ProjectMember(
            project_id=project_id, user_id=user_id, role=role
        )
        self.session.add(member)
        await self.session.commit()
        await self.session.refresh(member)
        return member

    async def update_project_member(
        self, project_id: UUID, user_id: UUID, role: Role
    ) -> ProjectMember | None:
        statement = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        member = (await self.session.execute(statement)).scalars().first()
        if not member:
            return None

        member.role = role
        self.session.add(member)
        await self.session.commit()
        await self.session.refresh(member)
        return member

    async def remove_project_member(
        self, project_id: UUID, user_id: UUID
    ) -> bool:
        statement = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        member = (await self.session.execute(statement)).scalars().first()
        if not member:
            return False

        await self.session.delete(member)
        await self.session.commit()
        return True

    async def update_project(
        self,
        project_id: UUID,
        project_update: ProjectUpdate,
        user: User,
    ) -> Project | None:
        project = await self.session.get(Project, project_id)
        if not project:
            return None

        if project.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the project owner can update the project",
            )

        project_data = project_update.model_dump(exclude_unset=True)
        for key, value in project_data.items():
            setattr(project, key, value)

        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def delete_project(self, project_id: UUID, user: User) -> bool:
        project = await self.session.get(Project, project_id)
        if not project:
            return False

        if project.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the project owner can delete the project",
            )

        await self.session.delete(project)
        await self.session.commit()
        return True


def get_project_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> ProjectService:
    return ProjectService(session)


project_service = get_project_service
ProjectServiceDep = Annotated[ProjectService, Depends(get_project_service)]
