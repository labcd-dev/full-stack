"""ORM models for authentication and permissions."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Table, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend_api.db.base import Base

user_actions = Table(
    "user_actions",
    Base.metadata,
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("action_id", ForeignKey("actions.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    actions: Mapped[list[Action]] = relationship(
        "Action",
        secondary=user_actions,
        back_populates="users",
        lazy="selectin",
    )

    def action_codes(self) -> list[str]:
        return sorted(action.code for action in self.actions)

    def has_action(self, code: str) -> bool:
        if self.is_admin:
            return True
        return any(action.code == code for action in self.actions)


class Action(Base):
    __tablename__ = "actions"
    __table_args__ = (UniqueConstraint("code", name="uq_actions_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, default="", nullable=False)

    users: Mapped[list[User]] = relationship(
        "User",
        secondary=user_actions,
        back_populates="actions",
        lazy="selectin",
    )
