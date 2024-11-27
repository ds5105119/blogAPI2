import datetime
from typing import Optional

from sqlalchemy import JSON, Boolean, DateTime, ForeignKeyConstraint, Index, Integer, PrimaryKeyConstraint, String, func
from sqlalchemy.ext.mutable import MutableSet
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.models.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    email: Mapped[str] = mapped_column(String(255))
    handle: Mapped[str] = mapped_column(String(255))
    password: Mapped[str] = mapped_column(String(255))

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
    deleted_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    resignation_reason: Mapped[Optional[str]] = mapped_column(String(255))

    profiles: Mapped["Profile"] = relationship("Profile", back_populates="users", uselist=False)


class Profile(Base):
    __tablename__ = "profiles"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="profiles_pk"),
        ForeignKeyConstraint(["user_id"], ["users.id"], name="profiles_user_id_fk", ondelete="CASCADE"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer)

    profile: Mapped[str] = mapped_column(String(255))
    bio: Mapped[Optional[str]] = mapped_column(String(255))
    link: Mapped[Optional[list]] = mapped_column(MutableSet.as_mutable(JSON))

    users: Mapped["User"] = relationship("User", back_populates="profiles")
