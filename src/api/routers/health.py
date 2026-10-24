from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from config.logger import Logger
from storage.connectors.db import get_db

router = APIRouter()

logger = Logger.get_logger(__name__)


@router.get("/check")
async def check():
    return "Is alive and running!"


@router.get("/db")
def check_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
    except Exception as exc:
        logger.error("La base de datos no responde: %s", exc)
        raise HTTPException(status_code=503, detail={"db": "error"})
    return {"db": "ok"}
