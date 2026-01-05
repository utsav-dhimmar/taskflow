from typing import Annotated, List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.main import get_session
from app.models.enums import ProjectPriority, ProjectStatus
from app.models.user import User
from app.routes.auth import get_current_user
from app.schema.task import TaskCreate, TaskResponse, TaskUpdate
from app.services.task_service import TaskService


router = APIRouter(tags=["tasks"])
task_service = TaskService()


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
):
    """
    Create a new task in the project
    """
    return await task_service.create_task(
        session, project_id, task_create, current_user
    )


@router.get("/projects/{project_id}/tasks", response_model=List[TaskResponse])
async def list_tasks(
    project_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
    status: Optional[ProjectStatus] = None,
    priority: Optional[ProjectPriority] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
):
    return await task_service.get_tasks_by_project(
        session, project_id, current_user, status, priority, page, limit
    )


@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def read_task(
    task_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    task = await task_service.get_task_by_id(session, task_id, current_user)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: UUID,
    task_update: TaskUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    task = await task_service.update_task(session, task_id, task_update, current_user)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    success = await task_service.delete_task(session, task_id, current_user)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return
