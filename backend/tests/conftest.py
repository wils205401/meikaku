import os

import pytest
from testcontainers.postgres import PostgresContainer
from alembic.config import Config
from alembic import command

from collections.abc import Generator

from sqlalchemy.orm import Session
from sqlalchemy.engine.base import Engine
from sqlalchemy import create_engine

from fastapi.testclient import TestClient

from app.main import app
from app.dependencies import get_db


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
    session = Session(bind=connection)

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
