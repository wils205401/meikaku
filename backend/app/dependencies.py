from fastapi import Depends
from sqlalchemy.orm import Session
from typing import Annotated
from app.core.database import DBSession


def get_db():
    db = DBSession()
    try:
        yield db
    finally:
        db.close()


SessionDep = Annotated[Session, Depends(get_db)]
