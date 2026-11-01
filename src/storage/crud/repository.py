import uuid
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

T = TypeVar("T")

class Repository(ABC, Generic[T]):
    @abstractmethod
    def create(self, entity: T) -> T | None:
        pass

    @abstractmethod
    def get(self, id: uuid.UUID) -> T | None:
        pass

    @abstractmethod
    def update(self, id: uuid.UUID, entity: T) -> T | None:
        pass

    @abstractmethod
    def delete(self, id: uuid.UUID) -> bool:
        pass