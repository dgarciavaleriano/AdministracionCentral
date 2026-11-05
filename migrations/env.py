"""Alembic compara las tablas de src/storage/entities/ con la base y aplica las migraciones."""

import logging

from alembic import context

from storage import entities  # noqa: F401  importarlas registra las tablas en Base
from storage.connectors.db import Base, engine

# Para ver en consola qué migraciones se aplican ("Running upgrade ...").
logging.basicConfig(format="%(message)s")
logging.getLogger("alembic").setLevel(logging.INFO)

with engine.connect() as connection:
    context.configure(connection=connection, target_metadata=Base.metadata)
    with context.begin_transaction():
        context.run_migrations()
