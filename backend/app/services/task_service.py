from collections.abc import Sequence
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.celery_app import celery_app
from app.core.logging import get_logger
from app.db.main import get_session
from app.db.models.enums import ProjectPriority, ProjectStatus, Role
from app.db.models.project import Project, ProjectMember
from app.db.models.task import Task
from app.db.models.user import User
from app.schemas.task import TaskCreate, TaskUpdate

logger = get_logger(__name__)


class TaskService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create_task(
        self,
        project_id: UUID,
        task_create: TaskCreate,
        user: User,
    ) -> Task:
        # Verify user is member of project
        statement = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user.id,
        )
        member = (await self.session.execute(statement)).scalars().first()
        if not member and user.role != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not a member of the project",
            )
        # if user is not a member then add it
        if not member:
            project_member = ProjectMember(
                project_id=project_id,
                user_id=user.id,
                role=Role.USER,
            )
            self.session.add(project_member)
            await self.session.commit()
            await self.session.refresh(project_member)

        db_task = Task(
            project_id=project_id,
            title=task_create.title,
            description=task_create.description,
            status=task_create.status,
            priority=task_create.priority,
            assigned_to=task_create.assigned_to,
            due_datetime=task_create.due_datetime,
            created_by=user.id,
        )
        self.session.add(db_task)
        await self.session.commit()
        await self.session.refresh(db_task)

        if db_task.assigned_to:
            assigned_user = await self.session.get(User, db_task.assigned_to)
            project = await self.session.get(Project, project_id)
            if assigned_user and project:
                celery_app.send_task(
                    "app.worker.send_task_assigned_email",
                    args=[assigned_user.email, db_task.title, project.name],
                )

        return db_task

    async def get_tasks_by_project(
        self,
        project_id: UUID,
        user: User,
        status_filter: ProjectStatus | None = None,
        priority_filter: ProjectPriority | None = None,
        page: int = 1,
        limit: int = 10,
    ) -> Sequence[Task]:
        # Verify membership
        member_check = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user.id,
        )
        if not (await self.session.execute(member_check)).scalars().first():
            # Check if owner
            project = await self.session.get(Project, project_id)
            if not project or project.owner_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Access denied",
                )

        statement = select(Task).where(Task.project_id == project_id)

        if status_filter:
            statement = statement.where(Task.status == status_filter)
        if priority_filter:
            statement = statement.where(Task.priority == priority_filter)

        statement = statement.offset((page - 1) * limit).limit(limit)

        result = (await self.session.execute(statement)).scalars()
        return result.all()

    async def get_task_by_id(self, task_id: UUID, user: User) -> Task | None:
        task = await self.session.get(Task, task_id)
        if not task:
            return None

        # Check permission (membership of project)
        # We need to join with project/members or do a separate check
        # Separate check:
        # 1. Get Project
        # 2. Check Member
        # Optimization: Join

        # Simple check for now:
        project_id = task.project_id

        # Check owner
        project = await self.session.get(Project, project_id)
        if project and project.owner_id == user.id:
            return task

        # Check member
        stat = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user.id,
        )
        if (await self.session.execute(stat)).scalars().first():
            return task

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    async def update_task(
        self,
        task_id: UUID,
        task_update: TaskUpdate,
        user: User,
    ) -> Task:
        task = await self.get_task_by_id(task_id, user)

        if not task:  # Should be caught by get_task_by_id or return None
            raise HTTPException(status_code=404, detail="Task not found")

        task_data = task_update.model_dump(exclude_unset=True)
        for key, value in task_data.items():
            setattr(task, key, value)

        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def delete_task(self, task_id: UUID, user: User) -> bool:
        task = await self.get_task_by_id(task_id, user)
        if not task:
            return False

        project = await self.session.get(Project, task.project_id)
        is_owner = project.owner_id == user.id if project else False
        is_creator = task.created_by == user.id

        if not (is_owner or is_creator):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the task creator or project owner can delete this task",
            )

        await self.session.delete(task)
        await self.session.commit()
        logger.info(f"Task deleted: {task.id}")
        return True


def get_task_service(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TaskService:
    return TaskService(session)


task_service = get_task_service
TaskServiceDep = Annotated[TaskService, Depends(get_task_service)]
