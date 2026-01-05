from typing import Optional, Sequence
from uuid import UUID

from fastapi import HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models.enums import ProjectPriority, ProjectStatus, Role
from app.models.project import Project, ProjectMember
from app.models.task import Task
from app.models.user import User
from app.schema.task import TaskCreate, TaskUpdate
from app.worker import send_task_assigned_email


class TaskService:
    async def create_task(
        self,
        session: AsyncSession,
        project_id: UUID,
        task_create: TaskCreate,
        user: User,
    ) -> Task:
        # Verify user is member of project
        statement = select(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.user_id == user.id
        )
        member = (await session.exec(statement)).first()
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
            session.add(project_member)
            await session.commit()
            await session.refresh(project_member)

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
        session.add(db_task)
        await session.commit()
        await session.refresh(db_task)

        if db_task.assigned_to:
            assigned_user = await session.get(User, db_task.assigned_to)
            project = await session.get(Project, project_id)
            if assigned_user and project:
                send_task_assigned_email.delay(
                    assigned_user.email, db_task.title, project.name
                )

        return db_task

    async def get_tasks_by_project(
        self,
        session: AsyncSession,
        project_id: UUID,
        user: User,
        status_filter: Optional[ProjectStatus] = None,
        priority_filter: Optional[ProjectPriority] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Sequence[Task]:
        # Verify membership
        member_check = select(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.user_id == user.id
        )
        if not (await session.exec(member_check)).first():
            # Check if owner
            project = await session.get(Project, project_id)
            if not project or project.owner_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
                )

        statement = select(Task).where(Task.project_id == project_id)

        if status_filter:
            statement = statement.where(Task.status == status_filter)
        if priority_filter:
            statement = statement.where(Task.priority == priority_filter)

        statement = statement.offset((page - 1) * limit).limit(limit)

        result = await session.exec(statement)
        return result.all()

    async def get_task_by_id(
        self, session: AsyncSession, task_id: UUID, user: User
    ) -> Optional[Task]:
        task = await session.get(Task, task_id)
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
        project = await session.get(Project, project_id)
        if project and project.owner_id == user.id:
            return task

        # Check member
        stat = select(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.user_id == user.id
        )
        if (await session.exec(stat)).first():
            return task

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
        )

    async def update_task(
        self,
        session: AsyncSession,
        task_id: UUID,
        task_update: TaskUpdate,
        user: User,
    ) -> Task:
        task = await self.get_task_by_id(session, task_id, user)

        if not task:  # Should be caught by get_task_by_id or return None
            raise HTTPException(status_code=404, detail="Task not found")

        task_data = task_update.model_dump(exclude_unset=True)
        for key, value in task_data.items():
            setattr(task, key, value)

        session.add(task)
        await session.commit()
        await session.refresh(task)
        return task

    async def delete_task(
        self, session: AsyncSession, task_id: UUID, user: User
    ) -> bool:
        task = await self.get_task_by_id(session, task_id, user)
        if not task:
            return False

        project = await session.get(Project, task.project_id)
        is_owner = project.owner_id == user.id if project else False
        is_creator = task.created_by == user.id

        if not (is_owner or is_creator):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the task creator or project owner can delete this task",
            )

        await session.delete(task)
        await session.commit()
        print(task)
        return True
