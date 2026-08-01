from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.main import get_session
from app.db.models.enums import ProjectPriority, ProjectStatus
from app.db.models.user import User
from app.routes.auth import get_current_user
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import TaskServiceDep

router = APIRouter(tags=["tasks"])


@router.post(
    "/projects/{project_id}/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_task(
    project_id: UUID,
    task_create: TaskCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    task_service: TaskServiceDep,
):
    """
    Create a new task in the project
    """
    return await task_service.create_task(project_id, task_create, current_user)


@router.get("/projects/{project_id}/tasks", response_model=list[TaskResponse])
async def list_tasks(
    project_id: UUID,
    task_service: TaskServiceDep,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    status: ProjectStatus | None = None,
    priority: ProjectPriority | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    return await task_service.get_tasks_by_project(
        project_id, current_user, status, priority, page, limit
    )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def read_task(
    task_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    task_service: TaskServiceDep,
):
    task = await task_service.get_task_by_id(task_id, current_user)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    task_service: TaskServiceDep,
):
    task = await task_service.update_task(task_id, task_update, current_user)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    task_service: TaskServiceDep,
):
    success = await task_service.delete_task(task_id, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
