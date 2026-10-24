"""Fixtures comunes. Los tests usan la base de datos del docker-compose, con las
migraciones aplicadas:

    docker compose up -d --wait db
    uv run python -m alembic upgrade head
"""

import pytest

from storage.connectors.db import SessionLocal


@pytest.fixture
def db():
    """Sesión para un test. Al acabar se deshace todo lo que el test haya guardado."""
    session = SessionLocal()
    yield session
    session.rollback()
    session.close()
