"""Configuración de Alembic.

`alembic.ini` tiene `prepend_sys_path = %(here)s/src`, por eso se pueden importar
`config.*` y `storage.*` desde aquí.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool
from sqlalchemy.engine import Connection

from config.settings import settings
from storage.base import Base

import storage.entities  # noqa: F401  registra las entidades en Base.metadata

config = context.config

# disable_existing_loggers=False: si no, silencia los loggers de la app.
if config.config_file_name is not None:
    fileConfig(config.config_file_name, disable_existing_loggers=False)

target_metadata = Base.metadata


def abortar_si_no_hay_cambios(migration_context, revision, directives) -> None:
    """Un fichero vacío suele ser una entidad sin importar, y eso `alembic check` no
    lo detecta: compara "sin tabla" contra "sin tabla" y le parece bien."""
    if not getattr(config.cmd_opts, "autogenerate", False):
        return
    if directives[0].upgrade_ops.is_empty():
        directives[:] = []
        raise SystemExit(
            "Nada que migrar: el modelo y la base ya coinciden.\n"
            "Si esperabas cambios, comprueba que la entidad nueva tenga su linea "
            "en entities/__init__.py y que el fichero este guardado."
        )


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # Desactivadas de fábrica: sin ellas, cambiar String(50) por String(100)
        # o tocar un server_default pasaría desapercibido.
        compare_type=True,
        compare_server_default=True,
        process_revision_directives=abortar_si_no_hay_cambios,
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
            poolclass=pool.NullPool,  # una migración es de usar y tirar
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
