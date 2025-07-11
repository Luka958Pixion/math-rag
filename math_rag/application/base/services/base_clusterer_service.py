from abc import ABC, abstractmethod
from uuid import UUID


class BaseClustererService(ABC):
    @abstractmethod
    def cluster(self, ids: list[UUID], embeddings: list[list[float]]) -> list[list[UUID]]:
        pass
