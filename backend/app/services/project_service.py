from typing import Optional, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import or_, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.enums import Role
from app.models.project import Project, ProjectMember
from app.models.user import User
from app.schema.project import ProjectCreate, ProjectUpdate


class ProjectService:
    async def create_project(
        self, session: AsyncSession, project_create: ProjectCreate, user: User
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
        session.add(db_project)
        await session.commit()
        await session.refresh(db_project)

        # project creator aka admin is also member
        member = ProjectMember(
            user_id=user.id, project_id=db_project.id, role=Role.ADMIN
        )
        session.add(member)
        await session.commit()

        return db_project

    async def get_projects_for_user(
        self, session: AsyncSession, user: User
    ) -> Sequence[Project]:
        # Get the all Project where user is member or owner
        statement = (
            select(Project)
            .join(
                ProjectMember,
                Project.id == ProjectMember.project_id,  # type: ignore
                # working but typing error
                isouter=True,
            )
            .join(
                User,
                ProjectMember.user_id == User.id,  # type: ignore
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

        result = await session.exec(statement)
        return result.all()

    async def get_project_by_id(
        self, session: AsyncSession, project_id: UUID, user: User
    ) -> Optional[Project]:
        project = await session.get(Project, project_id)
        if not project:
            return None

        if project.owner_id == user.id:
            return project

        statement = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user.id,
        )
        member = (await session.exec(statement)).first()
        if member:
            return project

        return None

    async def get_project_members(
        self, session: AsyncSession, project_id: UUID
    ) -> Sequence[ProjectMember]:
        statement = select(ProjectMember).where(ProjectMember.project_id == project_id)
        result = await session.exec(statement)
        return result.all()

    async def add_project_member(
        self, session: AsyncSession, project_id: UUID, user_id: UUID, role: Role
    ) -> ProjectMember:
        statement = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        existing = (await session.exec(statement)).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this project",
            )

        member = ProjectMember(project_id=project_id, user_id=user_id, role=role)
        session.add(member)
        await session.commit()
        await session.refresh(member)
        return member

    async def update_project_member(
        self, session: AsyncSession, project_id: UUID, user_id: UUID, role: Role
    ) -> Optional[ProjectMember]:
        statement = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        member = (await session.exec(statement)).first()
        if not member:
            return None

        member.role = role
        session.add(member)
        await session.commit()
        await session.refresh(member)
        return member

    async def remove_project_member(
        self, session: AsyncSession, project_id: UUID, user_id: UUID
    ) -> bool:
        statement = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )
        member = (await session.exec(statement)).first()
        if not member:
            return False

        await session.delete(member)
        await session.commit()
        return True

    async def update_project(
        self,
        session: AsyncSession,
        project_id: UUID,
        project_update: ProjectUpdate,
        user: User,
    ) -> Optional[Project]:
        project = await session.get(Project, project_id)
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

        session.add(project)
        await session.commit()
        await session.refresh(project)
        return project

    async def delete_project(
        self, session: AsyncSession, project_id: UUID, user: User
    ) -> bool:
        project = await session.get(Project, project_id)
        if not project:
            return False

        if project.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the project owner can delete the project",
            )

        await session.delete(project)
        await session.commit()
        return True
