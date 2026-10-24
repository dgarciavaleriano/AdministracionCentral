"""Tabla `plans`: límites de uso de cada plan de suscripción."""

import uuid

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Uuid, func

from storage.connectors.db import Base


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)

    max_drafts = Column(Integer, nullable=False)
    max_sessions_per_day = Column(Integer, nullable=False)
    history_retention_days = Column(Integer, nullable=False)

    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<Plan {self.name}>"
