from abc import ABC, abstractmethod

from math_rag.core.models import Index


class BaseIndexBuilderService(ABC):
    @abstractmethod
    async def build(index: Index):
        pass
