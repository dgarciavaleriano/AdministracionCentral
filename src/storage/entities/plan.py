"""Tabla `plans`: límites de uso por plan de suscripción."""

import datetime
import uuid

from sqlalchemy import Boolean, Integer, String, text
from sqlalchemy.orm import Mapped, mapped_column

from storage.connectors.db import Base


class Plan(Base):
    __tablename__ = "plans"

    # `text(...)` obligatorio: la cadena pelada se guardaría como valor literal.
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )

    name: Mapped[str] = mapped_column(String(100), unique=True)

    max_drafts: Mapped[int] = mapped_column(Integer)
    max_sessions_per_day: Mapped[int] = mapped_column(Integer)
    history_retention_days: Mapped[int] = mapped_column(Integer)

    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"))

    created_at: Mapped[datetime.datetime] = mapped_column(server_default=text("now()"))

    def __repr__(self) -> str:
        return f"<Plan {self.name}>"
