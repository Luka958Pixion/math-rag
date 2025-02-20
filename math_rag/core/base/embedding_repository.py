from abc import ABC, abstractmethod


class EmbeddingRepository(ABC):
    @abstractmethod
    def create_collection(self, name: str) -> bool:
        pass

    @abstractmethod
    def delete_collection(self, name: str) -> bool:
        pass
