from abc import ABC, abstractmethod


class FileBaseRepository(ABC):
    @abstractmethod
    def create_bucket(self, name: str):
        pass

    @abstractmethod
    def delete_bucket(self, name: str):
        pass
