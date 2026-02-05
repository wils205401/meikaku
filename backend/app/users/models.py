from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models import TimestampMixin, UUIDPrimaryKeyMixin


class User(
    Base,
    UUIDPrimaryKeyMixin,
    TimestampMixin,
):
    email: Mapped[str] = mapped_column(
        unique=True,
        index=True,
    )
    password_hash: Mapped[str]

    owned_workspaces: Mapped[list["Workspace"]] = relationship(  # noqa: F821
        back_populates="owner",
        cascade="all, delete-orphan",
    )

    # TODO - add a is_verified for when user has completed email verification

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, email={self.email!r})"
