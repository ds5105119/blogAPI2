import datetime
from typing import List, Optional

from sqlalchemy import (
    JSONB,
    Boolean,
    DateTime,
    ForeignKeyConstraint,
    Index,
    Integer,
    PrimaryKeyConstraint,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="users_pk"),
        Index("ix_users_email", "email", unique=True),
        Index("ix_users_handle", "handle", unique=True),
        Index("ix_users_is_active", "is_active"),
        Index("ix_users_is_deleted", "is_deleted"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    email: Mapped[str] = mapped_column(String(255))
    handle: Mapped[str] = mapped_column(String(255))
    password: Mapped[str] = mapped_column(String(255))

    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(DateTime, onupdate=func.now())
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
    user_id: Mapped[int] = mapped_column(Integer, nullable=True)

    profile: Mapped[str] = mapped_column(String(255))
    bio: Mapped[Optional[str]] = mapped_column(String(255))

    users: Mapped["User"] = relationship("User", back_populates="profiles")
