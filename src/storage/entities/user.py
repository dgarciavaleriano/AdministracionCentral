"""Tabla `users`. Los esquemas de la API (Pydantic) van aparte, en `src/models/`."""

import uuid

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, String, Text, Uuid, func

from storage.connectors.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)

    # Identidad. No guardamos la orientación sexual: dato especial del RGPD (decisión de equipo).
    name = Column(String(100), nullable=False)
    surname_1 = Column(String(100), nullable=False)
    surname_2 = Column(String(100))
    nif = Column(String(16), unique=True, nullable=False)
    birthdate = Column(Date, nullable=False)
    marital_status = Column(String(32))

    # Contacto
    email = Column(String(254), unique=True, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    phone = Column(String(20))
    fiscal_address = Column(Text)

    # Cuenta
    password_hash = Column(String(255), nullable=False)
    status = Column(String(32), default="active", nullable=False)
    plan_id = Column(Uuid, ForeignKey("plans.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User {self.email}>"
