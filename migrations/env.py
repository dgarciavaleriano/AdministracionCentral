"""Configuración de Alembic. Es la plantilla de `alembic init` con tres cambios:
la URL sale de settings, se importan las entidades y se apunta a Base.metadata."""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from config.settings import settings
from storage import entities  # noqa: F401  importarlas registra las tablas en Base
from storage.connectors.db import Base

config = context.config

# Logs de Alembic según alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# La URL de la base sale de settings (.env o variables de entorno), no de alembic.ini.
config.set_main_option("sqlalchemy.url", settings.database_url)

# Las tablas que Alembic compara con la base para generar las migraciones.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Modo offline (`alembic upgrade --sql`): escribe el SQL sin conectarse."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Modo normal: se conecta a la base y aplica las migraciones."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
