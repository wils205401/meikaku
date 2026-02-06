from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.schemas import UserRegister
from app.core.security import get_password_hash, verify_password
from app.users.models import User
from app.workspaces.service import create_default_workspace_for_user


def register_user(*, session: Session, user_register: UserRegister) -> User:
    """
    Register user.

    The registration process has two steps:
        1. Saves user email and hashed password in db.
        2. Creates a workspace for the user
    """
    user = User(
        email=user_register.email,
        password_hash=get_password_hash(user_register.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    create_default_workspace_for_user(session=session, user=user)

    return user


def authenticate_user(*, session: Session, email: str, password: str) -> User | None:
    """
    Authenticate the user by verifying the password provided matches the one in db.
    """
    user = get_user_by_email(session=session, email=email)

    if not user:
        return None

    if not verify_password(password, user.password_hash):
        return None

    return user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    """
    Get user if it exists in the database, else return None
    """
    stmt = select(User).where(User.email == email)
    return session.scalar(stmt)
