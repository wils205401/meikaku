from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class WorkspaceBase(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class WorkspaceCreate(WorkspaceBase):
    pass


class WorkspaceRead(WorkspaceBase):
    id: UUID
    created_at: datetime
