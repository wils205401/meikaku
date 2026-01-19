from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings


class Base(DeclarativeBase):
    pass


engine = create_engine(str(settings.DATABASE_URI))
DBSession = sessionmaker(bind=engine, autoflush=True, autocommit=False)
