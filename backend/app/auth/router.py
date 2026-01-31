from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.dependencies import SessionDep
from app.auth.schemas import UserRegister, UserPublic, Token
from app.core.security import create_access_token
from typing import Any, Annotated

from app.auth.service import get_user_by_email, register_user, authenticate_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserPublic)
def register(session: SessionDep, user_register: UserRegister) -> Any:
    """
    Create/register a new user
    """
    user = get_user_by_email(session=session, email=user_register.email)
    if user:
        raise HTTPException(
            status_code=400, detail="A user with this email already exists."
        )

    registered_user = register_user(session=session, user_register=user_register)

    return registered_user


@router.post("/login", response_model=Token)
def login(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Any:
    """
    OAuth2 compatible token login.

    Returns an access token for future requests.
    """
    user = authenticate_user(
        session=session, email=form_data.username, password=form_data.password
    )

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password.")

    return Token(access_token=create_access_token(user.id))
