"""Engine, sesiones y clase base de las entidades."""

import datetime
from collections.abc import Generator

from sqlalchemy import DateTime, MetaData, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from config.settings import settings

# Queda congelada en la primera migración: cambiarla después obliga a renombrar
# las restricciones a mano en todos los entornos.
NAMING_CONVENTION = {
    # `column_0_N_name` usa todas las columnas: sin esto, un índice en (a) y
    # otro en (a, b) generarían el mismo nombre y chocarían.
    "ix": "ix_%(table_name)s_%(column_0_N_name)s",
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",
    # Con esta plantilla, toda CheckConstraint debe llevar `name=`.
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    # Todo `Mapped[datetime]` se guarda como TIMESTAMPTZ. Sin esto el instante
    # dependería de la zona horaria de quien insertó.
    type_annotation_map = {
        datetime.datetime: DateTime(timezone=True),
    }


engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,
    pool_timeout=5,   # espera por un hueco LIBRE del pool; no limita el connect
    # Sin esto psycopg espera 130 s (su default) aunque el SO rechace la conexión
    # al instante: /health/db tardaría más de dos minutos en devolver el 503.
    connect_args={"connect_timeout": 5},
    echo=False,             # nunca True: volcaría datos personales al log
    # SQLAlchemy mete [parameters: {...}] en el str() de TODA excepción de BD,
    # da igual el echo. Un alta con email repetido dejaría el password_hash, el
    # teléfono y la dirección fiscal en el log. Con esto sale "[SQL parameters
    # hidden due to hide_parameters=True]".
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
