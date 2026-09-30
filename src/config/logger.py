import logging
from typing import Any, Optional
from abc import ABC, abstractmethod
from typing import Any, Optional

class Logger(ABC):

    @abstractmethod
    def info(self, message: str, **kwargs: Any) -> None:
        pass

    @abstractmethod
    def warn(self, message: str, **kwargs: Any) -> None:
        pass

    @abstractmethod
    def error(self, message: str, error: Optional[Exception] = None, **kwargs: Any) -> None:
        pass

    @abstractmethod
    def debug(self, message: str, **kwargs: Any) -> None:
        pass

class Logging(Logger):
    def __init__(self, name: str):
        self._logger = logging.getLogger(name)
        logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

    def info(self, message: str, **kwargs: Any) -> None:
        self._logger.info(f"{message} | context: {kwargs}" if kwargs else message)

    def warn(self, message: str, **kwargs: Any) -> None:
        self._logger.warning(f"{message} | context: {kwargs}" if kwargs else message)

    def error(self, message: str, error: Optional[Exception] = None, **kwargs: Any) -> None:
        msg = f"{message} | context: {kwargs}" if kwargs else message
        self._logger.error(msg, exc_info=error)

    def debug(self, message: str, **kwargs: Any) -> None:
        self._logger.debug(f"{message} | context: {kwargs}" if kwargs else message)