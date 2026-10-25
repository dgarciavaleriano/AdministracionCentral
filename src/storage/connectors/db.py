from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config.logger import Logger
from config.settings import settings

logger = Logger.get_logger(__name__)

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, autoflush=False)

# Clase base de la que heredan todas las tablas (src/storage/entities/).
Base = declarative_base()


def get_db():
    """Dependencia de FastAPI: abre una sesión por petición. Al terminar guarda los
    cambios (commit), o los deshace (rollback) si ha habido un error, y la cierra."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        logger.error("Error en la sesión de base de datos", exc_info=True)
        raise
    finally:
        db.close()
