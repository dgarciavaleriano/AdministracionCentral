"""Configuración del frontal.

Prioridad: variables de entorno > fichero ui/.env > valores por defecto.

Mismo patrón que `src/config/settings.py`, pero con su propio `.env`: el
frontal es un proyecto independiente de la API.
"""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parents[1]

# Valor de desarrollo. NiceGUI necesita un secreto para firmar
# app.storage.user, y sin él cualquier página que lea el tema revienta con
# RuntimeError: el frontal no arrancaría en un clon recién hecho. Que sea
# una constante y no un valor aleatorio es a propósito: con `reload=True`
# NiceGUI reimporta este módulo en un subproceso, y dos secretos distintos
# invalidarían la sesión en cada recarga.
SECRETO_DE_DESARROLLO = "dev-only-cambia-esto-en-produccion"

# Un secreto que está en el repositorio no es un secreto. main.py avisa con
# cualquiera de estos, no solo con el de arriba: si no, copiar ui/.env.example
# tal cual silenciaba el aviso dejando el valor de relleno, que es público.
SECRETOS_PUBLICOS = frozenset({
    SECRETO_DE_DESARROLLO,
    "cambia-esto-por-un-secreto-seguro",  # el de ui/.env.example
})


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        # Ruta absoluta al ui/.env. `load_dotenv()` sin ruta buscaba desde el
        # directorio de trabajo: si arrancabas desde otra carpeta no encontraba
        # el fichero y no avisaba, así que todo se quedaba a None.
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        # Sin esto, cualquier clave del .env no declarada aquí lanza ValidationError.
        extra="ignore",
    )

    # 127.0.0.1 y no "localhost": en Windows "localhost" resuelve primero a ::1
    # y la API publica solo en IPv4, así que cada conexión espera ~30 s.
    api_base_url: str = "http://127.0.0.1:8080"
    api_timeout: float = 5.0

    # Prefijo `ui_` a propósito. `HOST`/`PORT` son de la API (docker-compose se
    # las define a 0.0.0.0:8080), y `NICEGUI_HOST`/`NICEGUI_PORT` las escribe
    # NiceGUI en el entorno para el subproceso del modo reload.
    ui_host: str = "127.0.0.1"
    ui_port: int = 8000

    # En despliegue se define por entorno. main.py avisa mientras siga puesto
    # el de desarrollo.
    nicegui_storage_secret: str = SECRETO_DE_DESARROLLO


settings = Settings()
