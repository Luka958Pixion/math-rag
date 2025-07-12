from abc import ABC, abstractmethod
from uuid import UUID


class BaseGrouperService(ABC):
    @abstractmethod
    def group(self, ids: list[UUID], embeddings: list[list[float]]) -> list[list[UUID]]:
        pass
