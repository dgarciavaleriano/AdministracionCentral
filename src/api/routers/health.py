from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from config.logger import Logger
from storage.connectors.db import get_db

router = APIRouter()

logger = Logger.get_logger(__name__)


@router.get("/check")
async def check():
    return "Is alive and running!"


# Ruta final /health/db: app.py monta el router con prefix="/health".
# Función `def`, no `async def`: SQLAlchemy síncrono bloquearía el event loop.
@router.get("/db")
def check_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        # Sin este log, el 503 no deja rastro de por qué falló.
        logger.error("Health check de base de datos fallido: %s", exc)
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"db": "error"},
        ) from exc
    return {"db": "ok"}
