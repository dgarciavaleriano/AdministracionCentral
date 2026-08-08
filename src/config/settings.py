"""Configuración de la aplicación.

Prioridad: variables de entorno > fichero .env > valores por defecto.
"""

from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Ruta absoluta: alembic y pytest pueden lanzarse desde otro directorio.
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        # Sin esto, cualquier clave del .env no declarada aquí lanza ValidationError.
        extra="ignore",
    )

    # 127.0.0.1 y no "localhost": en Windows "localhost" resuelve primero a ::1
    # y docker publica solo en IPv4, así que cada conexión espera ~30 s.
    database_url: str = "postgresql+psycopg://app:app@127.0.0.1:5432/administracion"
    test_database_url: str = "postgresql+psycopg://app:app@127.0.0.1:5433/administracion_test"

    host: str = "localhost"
    port: int = 8080
    log_level: str = "INFO"
    api_version: str = "1.0.0"

    @field_validator("log_level")
    @classmethod
    def _normalizar_log_level(cls, v: str) -> str:
        return v.strip().upper()


settings = Settings()
