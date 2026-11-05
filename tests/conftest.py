"""Fixtures comunes. Los tests usan la base de datos del docker-compose, con las
migraciones aplicadas:

    docker compose up -d --wait db
    uv run python -m alembic upgrade head
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import app
from storage.connectors.db import engine, get_db


@pytest.fixture
def db():
    """Sesión para un test. Al acabar se deshace todo lo que se haya guardado,
    incluso con commit: el test entero va dentro de una transacción que no se
    confirma nunca, y cada commit se queda en un savepoint dentro de ella."""
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection, join_transaction_mode="create_savepoint")

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def client(db):
    """Cliente de la API que usa la sesión del test en lugar de get_db: así lo que
    guarden los endpoints también se deshace al acabar."""
    app.dependency_overrides[get_db] = lambda: db
    yield TestClient(app)
    app.dependency_overrides.clear()
