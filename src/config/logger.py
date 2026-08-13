from dotenv import load_dotenv
import os
import logging

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(levelname)s - %(message)s"
)

class Logger:
    @staticmethod
    def get_logger(name: str) -> logging.Logger:
        return logging.getLogger(name)