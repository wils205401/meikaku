from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.users.models import User
from app.workspaces.exceptions import (
    WorkspaceAlreadyExists,
    WorkspaceForbidden,
    WorkspaceNotFound,
)
from app.workspaces.models import Workspace


def create_workspace_for_user(
    *,
    session: Session,
    user: User,
    name: str,
) -> Workspace:
    """Creates a workspace for user."""
    workspace = Workspace(
        name=name,
        owner_id=user.id,
    )
    session.add(workspace)

    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise WorkspaceAlreadyExists() from exc

    session.refresh(workspace)

    return workspace


def create_default_workspace_for_user(
    *,
    session: Session,
    user: User,
) -> Workspace:
    """
    Creates a default workspace for user.

    This is intented to be used when registering a new user.
    """
    return create_workspace_for_user(session=session, user=user, name="My Workspace")


def get_all_workspaces_for_user(
    *,
    session: Session,
    user: User,
) -> Sequence[Workspace]:
    stmt = (
        select(Workspace)
        .where(Workspace.owner_id == user.id)
        .order_by(Workspace.updated_at.desc())
    )
    return session.scalars(stmt).all()


def get_workspace_for_user(
    *, session: Session, user: User, workspace_id: UUID
) -> Workspace:
    """
    Gets the requested workspace from the database for the user.
    """
    workspace = session.get(Workspace, workspace_id)

    if not workspace:
        raise WorkspaceNotFound(workspace_id=workspace_id)

    if workspace.owner_id != user.id:
        raise WorkspaceForbidden()

    return workspace
