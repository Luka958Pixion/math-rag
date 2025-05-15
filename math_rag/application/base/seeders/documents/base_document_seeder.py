from abc import ABC, abstractmethod


class BaseDocumentSeeder(ABC):
    @abstractmethod
    def seed(self, reset: bool):
        pass
