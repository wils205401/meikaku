import uuid

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.mixins import SoftDeleteMixin, TimestampMixin, UUIDPrimaryKeyMixin


class Workspace(
    Base,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
    SoftDeleteMixin,
):
    __table_args__ = (UniqueConstraint("owner_id", "name", name="uq_workspace_name"),)

    name: Mapped[str]
    owner_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"),
        index=True,
    )

    owner: Mapped["User"] = relationship(back_populates="owned_workspaces")  # noqa: F821

    def __repr__(self) -> str:
        return f"Workspace(id={self.id}, owner={self.owner.email}, name={self.name})"
