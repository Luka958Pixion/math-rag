from abc import ABC, abstractmethod


class ObjectBaseRepository(ABC):
    @abstractmethod
    def create_bucket(self, name: str):
        pass

    @abstractmethod
    def delete_bucket(self, name: str):
        pass
