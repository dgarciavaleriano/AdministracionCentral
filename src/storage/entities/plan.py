"""Tabla `plans`: límites de uso por plan de suscripción."""

from sqlalchemy import Boolean, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from storage.base import Base
from storage.entities.mixins import CreatedAt, UUIDPrimaryKey


class Plan(UUIDPrimaryKey, CreatedAt, Base):
    __tablename__ = "plans"

    name: Mapped[str] = mapped_column(String(100), unique=True)

    max_drafts: Mapped[int] = mapped_column(Integer)
    max_sessions_per_day: Mapped[int] = mapped_column(Integer)
    history_retention_days: Mapped[int] = mapped_column(Integer)

    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))

    def __repr__(self) -> str:
        return f"<Plan {self.name}>"
