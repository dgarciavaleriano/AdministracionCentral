"""Clase base de las entidades. Separada del engine: describir las tablas no
necesita driver de base de datos ni configuración."""

import datetime

from sqlalchemy import DateTime, MetaData
from sqlalchemy.orm import DeclarativeBase

# Congelada desde la primera migración: cambiarla obliga a renombrar las
# restricciones a mano en todos los entornos. `column_0_N_name` usa todas las
# columnas; con `column_0_name`, un índice en (a) y otro en (a, b) chocarían.
# Con la plantilla `ck`, toda CheckConstraint debe llevar `name=`.
NAMING_CONVENTION = {
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    # Sin timezone el instante dependería de la zona de quien insertó.
    type_annotation_map = {datetime.datetime: DateTime(timezone=True)}
