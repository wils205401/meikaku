from typing import Any
from uuid import UUID

from fastapi import APIRouter, status

from app.auth.dependencies import CurrentUser
from app.dependencies import SessionDep
from app.workspaces import service as workspace_service
from app.workspaces.schemas import WorkspaceCreate, WorkspaceRead

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post("", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
def create_workspace(
    session: SessionDep,
    user: CurrentUser,
    workspace_create: WorkspaceCreate,
) -> Any:
    return workspace_service.create_workspace_for_user(
        session=session,
        user=user,
        name=workspace_create.name,
    )


@router.get("", response_model=list[WorkspaceRead])
def get_workspaces(
    session: SessionDep,
    user: CurrentUser,
) -> Any:
    return workspace_service.get_all_workspaces_for_user(session=session, user=user)


@router.get("/{workspace_id}", response_model=WorkspaceRead)
def get_workspace(
    session: SessionDep,
    user: CurrentUser,
    workspace_id: UUID,
) -> Any:
    return workspace_service.get_workspace_for_user(
        session=session,
        user=user,
        workspace_id=workspace_id,
    )
