"""Columnas comunes a todas las tablas.

Se componen por herencia: `class User(UUIDPrimaryKey, Timestamped, Base)`.
Añadirlas a una entidad ya creada cambia el esquema y necesita migración.
"""

import datetime
import uuid

from sqlalchemy import text
from sqlalchemy.orm import Mapped, mapped_column


class UUIDPrimaryKey:
    # sort_order: sin él las columnas heredadas van al final y el id queda en
    # medio de la tabla. Las columnas propias de cada entidad usan el 0.
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        # `text(...)` obligatorio: la cadena pelada se guardaría como valor literal.
        server_default=text("gen_random_uuid()"),
        sort_order=-100,
    )


class CreatedAt:
    created_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("now()"), sort_order=100
    )


class Timestamped(CreatedAt):
    # `onupdate` no genera DDL: un UPDATE escrito a mano no toca esta columna.
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=text("now()"), onupdate=text("now()"), sort_order=101
    )
