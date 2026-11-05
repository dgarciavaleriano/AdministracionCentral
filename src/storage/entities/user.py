"""Tabla `users`. Los esquemas de la API (Pydantic) van aparte, en `src/models/`."""

import uuid

from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, String, Uuid, func

from storage.connectors.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Uuid, primary_key=True, default=uuid.uuid4)

    # Identidad. No guardamos la orientación sexual: dato especial del RGPD (decisión de equipo).
    name = Column(String, nullable=False)
    surname_1 = Column(String, nullable=False)
    surname_2 = Column(String)
    nif = Column(String, unique=True, nullable=False)
    birthdate = Column(Date, nullable=False)
    marital_status = Column(String)

    # Contacto
    email = Column(String, unique=True, nullable=False)
    email_verified = Column(Boolean, default=False, nullable=False)
    phone = Column(String)
    fiscal_address = Column(String)

    # Cuenta
    password_hash = Column(String, nullable=False)
    status = Column(String, default="active", nullable=False)
    plan_id = Column(Uuid, ForeignKey("plans.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<User {self.email}>"
