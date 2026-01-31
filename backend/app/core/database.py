from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(
    str(settings.DATABASE_URI),
    pool_pre_ping=True,  # avoids broken connections in long running containers
)
DBSession = sessionmaker(bind=engine, autoflush=True, autocommit=False)
