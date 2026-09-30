import uvicorn

from config.logger import Logging
from config.settings import settings

logging = Logging(__name__)

if __name__ == "__main__":
    logging.info(f"Starting server on {settings.host}:{settings.port}")
    uvicorn.run("app:app", host=settings.host, port=settings.port)
