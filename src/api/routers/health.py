from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session

from storage.connectors.db import get_db

router: APIRouter = APIRouter()

@router.get("/check")
async def check():
    return "Is alive and running!"


# Ruta final /health/db: app.py ya monta el router con prefix="/health".
# Función `def`, no `async def`: SQLAlchemy síncrono bloquearía el event loop.
@router.get("/db")
def check_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))  # text() obligatorio en SQLAlchemy 2.0
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={"db": "error"},
        )
    return {"db": "ok"}
