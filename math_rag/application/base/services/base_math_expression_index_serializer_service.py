from abc import ABC, abstractmethod
from uuid import UUID


class BaseMathExpressionIndexSerializerService(ABC):
    @abstractmethod
    async def serialize(self):
        pass
