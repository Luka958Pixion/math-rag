from abc import ABC, abstractmethod

from math_rag.core.models import Index


class BaseDatasetBuilderService(ABC):
    @abstractmethod
    async def build(self, index: Index):
        pass
