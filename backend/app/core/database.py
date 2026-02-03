from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, declared_attr, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """Shared base for all ORM models."""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"


engine = create_engine(
    str(settings.DATABASE_URI),
    pool_pre_ping=True,  # avoids broken connections in long running containers
)
DBSession = sessionmaker(bind=engine, autoflush=True, autocommit=False)
