from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import service as auth_service
from app.auth.schemas import UserRegister
from app.core.security import verify_password
from app.users.models import User
from app.workspaces.models import Workspace


class TestRegister:
    """Test the /register endpoint"""

    def test_register_user(self, client: TestClient, db_session: Session) -> None:
        """
        Test register user

        Send a post request to register a new user. Check:
            - response status code is 200
            - query the db and check user exists
            - query the db and check that email in db is the same as the one sent
        """
        # Arrange
        request_payload = {
            "email": "testuser@example.com",
            "password": "testuser",
        }
        # Act
        response = client.post(
            "/auth/register",
            json=request_payload,
        )

        # Assert
        # Check response code
        assert response.status_code == 200

        # Check response payload
        created_user: dict = response.json()
        assert set(created_user.keys()) == {"id", "email"}
        assert created_user["email"] == request_payload["email"]

        # Check user in db
        user = db_session.execute(
            select(User).where(User.id == created_user["id"])
        ).scalar()

        assert user
        assert user.email == request_payload["email"]
        password_matches = verify_password(
            request_payload["password"], user.password_hash
        )
        assert password_matches

    def test_register_user_already_exists(
        self, client: TestClient, db_session: Session
    ) -> None:
        """
        Test register user where user already exists
        """
        # Arrange
        email = "testuser@example.com"
        # First register a user
        user_register = UserRegister(email=email, password="testuser")
        auth_service.register_user(session=db_session, user_register=user_register)

        # Act
        # Register a new user with the same email
        response = client.post(
            "/auth/register",
            json={
                "email": email,
                "password": "anotheruser",
            },
        )

        # Assert
        # Check response code
        assert response.status_code == 400
        assert response.json()["detail"] == "A user with this email already exists."

    def test_workspace_created_on_user_registration(
        self, client: TestClient, db_session: Session
    ) -> None:
        # Arrange
        request_payload = {
            "email": "testuser@example.com",
            "password": "testuser",
        }
        # Act
        response = client.post(
            "/auth/register",
            json=request_payload,
        )

        # Assert
        # Check response code
        assert response.status_code == 200

        created_user: dict = response.json()

        # Check workspace in db
        workspace = db_session.execute(
            select(Workspace).where(Workspace.owner_id == created_user["id"])
        ).scalar()

        assert workspace
        assert workspace.name == "My Workspace"

        # Check user has owned workspace
        user = db_session.execute(
            select(User).where(User.id == created_user["id"])
        ).scalar()

        assert user
        assert user.owned_workspaces == [workspace]


class TestLogin:
    """Test the /login endpoint"""

    def test_user_login(self, client: TestClient, db_session: Session) -> None:
        """
        Test user login

        Send a post request to login a user. Check:
            - response status code is 200
            - an access token is returned
        """
        # Arrange
        email = "testuser@example.com"
        password = "testuser"

        # First register a user
        user_register = UserRegister(email=email, password=password)
        auth_service.register_user(session=db_session, user_register=user_register)

        # Act
        response = client.post(
            "/auth/login",
            data={"username": email, "password": password},
        )

        # Assert
        # Check response code
        assert response.status_code == 200

        # Check response payload
        token = response.json()
        assert token["access_token"]
        assert token["token_type"] == "bearer"

    def test_user_login_invalid_credentials(
        self, client: TestClient, db_session: Session
    ) -> None:
        # Arrange
        email = "testuser@example.com"
        password = "testuser"

        # First register a user
        user_register = UserRegister(email=email, password=password)
        auth_service.register_user(session=db_session, user_register=user_register)

        # Act
        # Case 1: Wrong email
        response = client.post(
            "/auth/login",
            data={"username": "anotheruser@example.com", "password": password},
        )

        assert response.status_code == 400
        assert response.json()["detail"] == "Incorrect username or password."

        # Case 2: Wrong password
        response = client.post(
            "/auth/login",
            data={"username": email, "password": "wrong_password"},
        )

        # Assert
        # Check response code
        assert response.status_code == 400
        assert response.json()["detail"] == "Incorrect username or password."
