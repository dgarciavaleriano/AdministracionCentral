"""Fixtures de pytest-alembic.

Los tests de migraciones corren contra `db_test` (puerto 5433), NUNCA contra la
base de desarrollo: `test_up_down_consistency` hace `downgrade` hasta base, o
sea DROP de todas las tablas.

Levantar antes:  docker compose up -d --wait db_test
"""

from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

from config.settings import settings

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def alembic_config():
    # pytest-alembic resuelve estas rutas contra el directorio de trabajo, no
    # contra el rootdir de pytest: las forzamos absolutas.
    return {
        "file": str(ROOT / "alembic.ini"),
        "script_location": str(ROOT / "migrations"),
    }


@pytest.fixture
def alembic_engine():
    # Las variables de entorno ganan al .env, así que basta un TEST_DATABASE_URL
    # mal puesto para que estos tests dropeen la base de trabajo.
    if settings.test_database_url == settings.database_url:
        pytest.fail(
            f"TEST_DATABASE_URL apunta a la misma base que DATABASE_URL "
            f"({settings.database_url}): estos tests harían DROP TABLE sobre ella."
        )

    # Sin connect_timeout, con db_test parada pytest se cuelga 130 s sin imprimir nada.
    engine = create_engine(
        settings.test_database_url, connect_args={"connect_timeout": 5}
    )
    try:
        with engine.connect():
            pass
    except OperationalError as exc:
        engine.dispose()
        pytest.fail(
            f"No hay base de datos en {settings.test_database_url}\n"
            f"Arranca:  docker compose up -d --wait db_test\n({exc.orig})"
        )

    try:
        yield engine  # migrations/env.py lo recoge en config.attributes["connection"]
    finally:
        engine.dispose()
