"""Comprueba el cableado get_db -> SessionLocal -> engine.

Los tests de pytest-alembic usan su propio engine y no tocan `db.py`: sin este
test, un `get_db` roto no lo detectaría nadie.
"""

import pytest
from fastapi.testclient import TestClient

from app import app

# Usa la base a la que apunte DATABASE_URL, porque el engine se construye al
# importar `db.py`. Solo hace SELECT 1, es inocuo.
pytestmark = pytest.mark.db


def test_health_db_ok():
    with TestClient(app) as client:
        response = client.get("/health/db")

    assert response.status_code == 200
    assert response.json() == {"db": "ok"}
