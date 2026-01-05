from typing import Annotated, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.db.main import get_session
from app.models.enums import Role
from app.models.project import Project, ProjectMember
from app.models.user import User
from app.routes.auth import get_current_user
from app.schema.project import ProjectCreate, ProjectResponse, ProjectUpdate
from app.schema.project_member import (
    ProjectMemberCreate,
    ProjectMemberResponse,
    ProjectMemberUpdate,
)
from app.services.project_service import ProjectService

router = APIRouter(prefix="/projects", tags=["projects"])
project_service = ProjectService()


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_create: ProjectCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Create a new project
    """
    # only admin can create projects
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create projects",
        )
    return await project_service.create_project(session, project_create, current_user)


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    List all projects for the current user
    """
    return await project_service.get_projects_for_user(session, current_user)


@router.get("/{project_id}", response_model=ProjectResponse)
async def read_project(
    project_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    project = await project_service.get_project_by_id(session, project_id, current_user)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: UUID,
    project_update: ProjectUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    project = await project_service.update_project(
        session, project_id, project_update, current_user
    )
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    success = await project_service.delete_project(session, project_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return


async def check_project_admin_permission(
    session: AsyncSession, project_id: UUID, user_id: UUID
):
    """
    Check if user is Owner or Admin of the project.
    """
    project = await project_service.get_project_by_id(
        session, project_id, User(id=user_id)
    )

    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.owner_id == user_id:
        return True

    member = await session.exec(
        select(ProjectMember).where(
            ProjectMember.project_id == project_id, ProjectMember.user_id == user_id
        )
    )
    member = member.first()
    if member and member.role == Role.ADMIN:
        return True

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Insufficient permissions (Project Admin required)",
    )


@router.post("/{project_id}/members", response_model=ProjectMemberResponse)
async def add_project_member_endpoint(
    project_id: UUID,
    member_create: ProjectMemberCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Add a new member to the project
    """
    await check_project_admin_permission(session, project_id, current_user.id)
    return await project_service.add_project_member(
        session, project_id, member_create.user_id, member_create.role
    )


@router.get("/{project_id}/members", response_model=List[ProjectMemberResponse])
async def list_project_members(
    project_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    List all members of the project
    """
    # Verify user can access project
    project = await project_service.get_project_by_id(session, project_id, current_user)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    return await project_service.get_project_members(session, project_id)


@router.patch("/{project_id}/members/{user_id}", response_model=ProjectMemberResponse)
async def update_project_member_role(
    project_id: UUID,
    user_id: UUID,
    member_update: ProjectMemberUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Update the project member role
    """
    await check_project_admin_permission(session, project_id, current_user.id)
    member = await project_service.update_project_member(
        session, project_id, user_id, member_update.role
    )
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return member


@router.delete(
    "/{project_id}/members/{user_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_project_member(
    project_id: UUID,
    user_id: UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_session)],
):
    """
    Remove the project member from the project
    """
    await check_project_admin_permission(session, project_id, current_user.id)
    success = await project_service.remove_project_member(session, project_id, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Member not found")
    return
