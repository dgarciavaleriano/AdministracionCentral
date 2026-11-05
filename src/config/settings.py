"""Configuración de la API: variables de entorno > fichero .env > valores por defecto."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # extra="ignore": que una clave del .env que no esté aquí no rompa el arranque.
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # 127.0.0.1 y no localhost: en Windows, localhost tarda ~30 s en llegar a Docker.
    database_url: str = "postgresql+psycopg://app:app@127.0.0.1:5432/administracion"

    host: str = "localhost"
    port: int = 8080
    log_level: str = "INFO"
    api_version: str = "1.0.0"


settings = Settings()
