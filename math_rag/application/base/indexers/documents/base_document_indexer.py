from abc import ABC, abstractmethod


class BaseDocumentIndexer(ABC):
    @abstractmethod
    def index(self, reset: bool):
        pass
