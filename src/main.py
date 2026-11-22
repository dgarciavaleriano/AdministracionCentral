import uvicorn

from config.logger import Logger
from config.settings import settings

logger = Logger.get_logger(__name__)

if __name__ == "__main__":
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    uvicorn.run("app:app", host=settings.host, port=settings.port)
