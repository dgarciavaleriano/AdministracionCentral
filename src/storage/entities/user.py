"""Tabla `users`.

No confundir con `src/models/user.py`, que son los esquemas Pydantic de la API.

No incluye `sexual_orientation`: categoría especial del art. 9 RGPD, decisión de equipo.
"""

import datetime
import uuid

from sqlalchemy import Boolean, Date, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import Mapped, mapped_column

from storage.connectors.db import Base


class User(Base):
    __tablename__ = "users"

    # `text(...)` obligatorio: la cadena pelada se guardaría como valor literal.
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, server_default=text("gen_random_uuid()")
    )

    # --- Identidad ---
    name: Mapped[str] = mapped_column(String(100))
    surname_1: Mapped[str] = mapped_column(String(100))
    surname_2: Mapped[str | None] = mapped_column(String(100))  # extranjeros
    nif: Mapped[str] = mapped_column(String(16), unique=True)   # NIF y NIE, sin validar aún
    birthdate: Mapped[datetime.date] = mapped_column(Date)
    marital_status: Mapped[str | None] = mapped_column(String(32))

    # --- Contacto ---
    email: Mapped[str] = mapped_column(String(254), unique=True)
    email_verified: Mapped[bool] = mapped_column(Boolean, server_default=text("false"))
    phone: Mapped[str | None] = mapped_column(String(20))
    fiscal_address: Mapped[str | None] = mapped_column(Text)

    # --- Cuenta ---
    password_hash: Mapped[str] = mapped_column(String(255))  # bcrypt ocupa 60
    # ondelete va en ForeignKey, NUNCA en relationship(): relationship no emite DDL.
    # RESTRICT y no CASCADE: la supresión es un proceso de anonimización controlado.
    plan_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("plans.id", ondelete="RESTRICT"), index=True
    )
    avatar_key: Mapped[str | None] = mapped_column(String(512))  # clave del object storage

    # --- Ciclo de vida ---
    # Valores previstos: active | erasure_requested | anonymized
    status: Mapped[str] = mapped_column(String(32), server_default=text("'active'"))
    anonymized_at: Mapped[datetime.datetime | None] = mapped_column()

    # --- Datos semiestructurados ---
    # MutableDict: sin él, `user.preferences["x"] = 1` + commit() NO emite UPDATE
    # y el cambio se pierde sin error. Solo rastrea el primer nivel.
    # none_as_null: sin él, asignar None guarda el literal JSON `null`, que pasa
    # el NOT NULL y se relee como None en vez de dict.
    preferences: Mapped[dict] = mapped_column(
        MutableDict.as_mutable(JSONB(none_as_null=True)),
        server_default=text("'{}'::jsonb"),
    )

    # --- Auditoría ---
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=text("now()"))
    # `onupdate` no genera DDL: un UPDATE escrito a mano no toca esta columna.
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("now()"), onupdate=text("now()")
    )

    def __repr__(self) -> str:
        return f"<User {self.email}>"
