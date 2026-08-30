"""Engine, pool de conexiones y sesiones. La clase base está en `storage/base.py`."""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from config.settings import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,
    pool_timeout=5,  # espera por un hueco LIBRE del pool; no limita el connect
    # Sin connect_timeout manda el sistema operativo: ~130 s agotando reintentos
    # TCP cuando los paquetes se pierden.
    connect_args={"connect_timeout": 5},
    echo=False,  # nunca True: volcaría datos personales al log
    # SQLAlchemy mete [parameters: {...}] en el str() de toda excepción de BD, con
    # echo o sin él: un email repetido dejaría el password_hash en el log.
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
