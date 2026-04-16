import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import service as auth_service
from app.auth.schemas import UserRegister
from app.workspaces import service as workspace_service
from app.workspaces.exceptions import WorkspaceAlreadyExists, WorkspaceForbidden
from app.workspaces.models import Workspace


def test_create_workspace_for_user(db_session: Session) -> None:
    # Create a User
    user_register = UserRegister(
        email="testuser@example.com",
        password="testuser",
    )
    user = auth_service.register_user(session=db_session, user_register=user_register)

    # Create a workspace
    workspace_name = "Test User's Workspace"
    workspace = workspace_service.create_workspace_for_user(
        session=db_session, user=user, name=workspace_name
    )

    assert workspace.name == workspace_name
    assert workspace.owner_id == user.id
    assert workspace.owner == user

    workspace_in_db = db_session.execute(
        select(Workspace).where(Workspace.id == workspace.id)
    ).scalar()

    assert workspace_in_db
    assert workspace_in_db.name == workspace_name
    assert workspace.owner_id == user.id
    assert workspace.owner == user


def test_no_duplicate_workspace_names_for_user(db_session: Session) -> None:
    # Create a User
    user_register = UserRegister(
        email="testuser@example.com",
        password="testuser",
    )
    user = auth_service.register_user(session=db_session, user_register=user_register)

    # Create a workspace
    workspace_name = "Test User's Workspace"
    workspace = workspace_service.create_workspace_for_user(
        session=db_session, user=user, name=workspace_name
    )

    # Create another workspace with the same name
    with pytest.raises(WorkspaceAlreadyExists):
        workspace_service.create_workspace_for_user(
            session=db_session, user=user, name=workspace_name
        )

    workspace_in_db = (
        db_session.execute(select(Workspace).where(Workspace.id == workspace.id))
        .scalars()
        .all()
    )

    breakpoint()

    assert len(workspace_in_db) == 1


def test_get_all_workspaces_for_user(db_session: Session) -> None:
    # Create a user
    user_register = UserRegister(
        email="user1@example.com",
        password="password1",
    )
    user = auth_service.register_user(session=db_session, user_register=user_register)

    # User already has a workspace by default
    # Create a new one
    workspace_service.create_workspace_for_user(
        session=db_session, user=user, name="Another Workspace"
    )

    # Get all workspaces for user
    workspaces = workspace_service.get_all_workspaces_for_user(
        session=db_session,
        user=user,
    )

    # Assert user has two workspaces
    assert len(workspaces) == 2


def test_get_workspace_for_user(db_session: Session) -> None:
    # Create two users
    user_1_register = UserRegister(
        email="user1@example.com",
        password="password1",
    )
    user_2_register = UserRegister(
        email="user2@example.com",
        password="password2",
    )

    user_1 = auth_service.register_user(
        session=db_session, user_register=user_1_register
    )
    user_2 = auth_service.register_user(
        session=db_session, user_register=user_2_register
    )

    # Create workspace for user 1
    workspace = workspace_service.create_workspace_for_user(
        session=db_session, user=user_1, name="User 1's Workspace"
    )

    # Assert user 1 can access workspace
    assert workspace_service.get_workspace_for_user(
        session=db_session, user=user_1, workspace_id=workspace.id
    )
    # Assert user 2 cannot access workspace
    with pytest.raises(WorkspaceForbidden):
        assert workspace_service.get_workspace_for_user(
            session=db_session, user=user_2, workspace_id=workspace.id
        )
