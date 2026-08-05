"""Comprueba el cableado get_db -> SessionLocal -> engine.

Los tests de pytest-alembic usan su propio engine y no tocan `db.py`: sin este
test, un `get_db` roto no lo detectaría nadie.
"""

import pytest
from fastapi.testclient import TestClient

from app import app

# El engine se construye al importar `db.py`, así que este test usa la base a la
# que apunte DATABASE_URL. Solo hace SELECT 1, es inocuo.
pytestmark = pytest.mark.db


def test_health_db_ok():
    with TestClient(app) as client:
        respuesta = client.get("/health/db")

    assert respuesta.status_code == 200
    assert respuesta.json() == {"db": "ok"}
