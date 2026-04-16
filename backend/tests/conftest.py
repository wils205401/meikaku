import os
from collections.abc import Generator

import pytest
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.orm import Session
from testcontainers.postgres import PostgresContainer

from alembic import command
from app.auth.schemas import UserRegister
from app.auth.service import register_user
from app.dependencies import get_db
from app.main import app


@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    with PostgresContainer("postgres:16", driver="psycopg") as postgres:
        yield postgres


@pytest.fixture(scope="session")
def database_url(postgres_container: PostgresContainer) -> str:
    return postgres_container.get_connection_url()


@pytest.fixture(scope="session")
def alembic_config(database_url: str) -> Generator[Config, None, None]:
    config = Config("alembic.ini")

    # Set test database url
    os.environ["TEST_DATABASE_URL"] = database_url
    yield config
    os.environ.pop("TEST_DATABASE_URL")


@pytest.fixture(scope="session", autouse=True)
def run_alembic_migrations(alembic_config: Config) -> None:
    command.upgrade(alembic_config, "head")


@pytest.fixture(scope="session")
def engine(database_url: str) -> Generator[Engine, None, None]:
    """
    SQLAlchemy engine fixture for tests.

    Creates tables once per test session and drops tables
    after all tests.
    """
    engine = create_engine(database_url, pool_pre_ping=True)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(engine: Engine) -> Generator[Session, None, None]:
    """
    Creates a new SQLAlchemy session for a test, bound to a transaction
    that is rolled back at the end.
        - Each test runs in a rolled back transaction
        - Ensures test isolation
    """
    # Create a connection to the database
    connection = engine.connect()
    # Start a transaction
    transaction = connection.begin()
    # Bind a session to the connection
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    FastAPI Test Client Fixture.

    Overrides get_db dependency with the SQLite DB for testing.
    """

    def override_get_db():
        yield db_session

    # Override FastAPI dependency
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as client:
        yield client

    # Clear override after test
    app.dependency_overrides.clear()


@pytest.fixture
def user_a_token_headers(client: TestClient, db_session: Session) -> dict[str, str]:
    """
    Fixture for creating a login session with User A
    """
    user_a_email = "user_a@example.com"
    user_a_password = "user_a_password"
    # Create a user
    user_register = UserRegister(
        email=user_a_email,
        password=user_a_password,
    )
    register_user(session=db_session, user_register=user_register)

    # Login as the user and get token
    login_data = {
        "username": user_a_email,
        "password": user_a_password,
    }
    response = client.post("/auth/login", data=login_data)
    access_token = response.json()["access_token"]
    header = {"Authorization": f"Bearer {access_token}"}

    return header


@pytest.fixture
def user_b_token_headers(client: TestClient, db_session: Session) -> dict[str, str]:
    """
    Fixture for creating a login session with User A
    """
    user_b_email = "user_b@example.com"
    user_b_password = "user_b_password"
    # Create a user
    user_register = UserRegister(
        email=user_b_email,
        password=user_b_password,
    )
    register_user(session=db_session, user_register=user_register)

    # Login as the user and get token
    login_data = {
        "username": user_b_email,
        "password": user_b_password,
    }
    response = client.post("/auth/login", data=login_data)
    access_token = response.json()["access_token"]
    header = {"Authorization": f"Bearer {access_token}"}

    return header
