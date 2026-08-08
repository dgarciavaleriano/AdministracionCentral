"""Engine, sesiones y clase base de las entidades."""

import datetime
from collections.abc import Generator

from sqlalchemy import DateTime, MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config.settings import settings

# Congelada desde la primera migración: cambiarla obliga a renombrar las
# restricciones a mano en todos los entornos.
# `column_0_N_name` usa todas las columnas: con `column_0_name`, un índice en (a)
# y otro en (a, b) generarían el mismo nombre y chocarían.
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

    # Sin `timezone=True` el instante dependería de la zona horaria de quien insertó.
    type_annotation_map = {
        datetime.datetime: DateTime(timezone=True),
    }


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,
    pool_timeout=5,  # espera por un hueco LIBRE del pool; no limita el connect
    # Sin connect_timeout no hay límite propio y manda el sistema operativo:
    # ~130 s agotando reintentos TCP cuando los paquetes se pierden (contenedor
    # caído, IP equivocada). /health/db tardaría eso en devolver el 503.
    connect_args={"connect_timeout": 5},
    echo=False,  # nunca True: volcaría datos personales al log
    # SQLAlchemy mete [parameters: {...}] en el str() de TODA excepción de BD, con
    # echo o sin él: un alta con email repetido dejaría el password_hash, el
    # teléfono y la dirección fiscal en el log.
    hide_parameters=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    """Dependencia de FastAPI. Usar en endpoints `def`, no `async def`."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
