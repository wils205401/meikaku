from sqlalchemy.orm import Session

from app.auth import service as auth_service
from app.auth.schemas import UserRegister


def test_register_user(db_session: Session) -> None:
    email = "testuser@example.com"
    password = "testuser"

    user_register = UserRegister(email=email, password=password)
    user = auth_service.register_user(session=db_session, user_register=user_register)

    assert user.email == email
    assert hasattr(user, "password_hash")


def test_authenticate_user(db_session: Session) -> None:
    email = "testuser@example.com"
    password = "testuser"

    # Case 1: User doesn't exist
    authenticated_user = auth_service.authenticate_user(
        session=db_session, email=email, password=password
    )
    assert authenticated_user is None

    # Let's register a user
    user_register = UserRegister(email=email, password=password)
    auth_service.register_user(session=db_session, user_register=user_register)

    # Case 2: Password doesn't match
    authenticated_user = auth_service.authenticate_user(
        session=db_session, email=email, password="wrongpassword"
    )
    assert authenticated_user is None

    # Case 3: User exists
    authenticated_user = auth_service.authenticate_user(
        session=db_session, email=email, password=password
    )
    assert authenticated_user is not None


def test_get_user_by_email(db_session: Session) -> None:
    email = "testuser@example.com"
    password = "testuser"

    # Let's register a user
    user_register = UserRegister(email=email, password=password)
    registered_user = auth_service.register_user(
        session=db_session, user_register=user_register
    )

    # Case 1: User doesn't exist
    user = auth_service.get_user_by_email(
        session=db_session, email="anotheruser@example.com"
    )
    assert user is None

    # Case 2: User exists
    user = auth_service.get_user_by_email(session=db_session, email=email)
    assert user is not None
    assert user is registered_user
