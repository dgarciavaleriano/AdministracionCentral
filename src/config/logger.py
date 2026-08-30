import logging

from config.settings import settings

logging.basicConfig(
    level=settings.log_level,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class Logger:
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        return logging.getLogger(name)
