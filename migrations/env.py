"""Configuración de Alembic.

`alembic.ini` tiene `prepend_sys_path = %(here)s/src`, por eso se puede
importar `config.*` y `storage.*` desde aquí.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Connection

from config.settings import settings
from storage.connectors.db import Base

# Registra todas las entidades en Base.metadata.
import storage.entities  # noqa: F401

config = context.config

# `disable_existing_loggers=False`: si no, silencia los loggers de la app.
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        compare_server_default=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    # pytest-alembic inyecta aquí su conexión. Sin leer este atributo, los tests
    # migrarían -y harían `downgrade base`- sobre la base de DESARROLLO.
    connectable = config.attributes.get("connection", None)

    if connectable is None:
        connectable = create_engine(
            settings.database_url,
            poolclass=pool.NullPool,
            # Sin esto, con la base caída cualquier comando de alembic se queda
            # colgado 130 s (el default de psycopg) en vez de fallar.
            connect_args={"connect_timeout": 5},
        )

    if isinstance(connectable, Connection):
        do_run_migrations(connectable)
    else:
        with connectable.connect() as connection:
            do_run_migrations(connection)


def run_migrations_offline() -> None:
    """Modo `--sql`: no conecta, solo imprime el SQL."""
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
