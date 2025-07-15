from abc import ABC, abstractmethod
from uuid import UUID


class BaseMathExpressionRelationshipSerializerService(ABC):
    @abstractmethod
    async def serialize(self, math_expression_relationship_ids: list[UUID]) -> str:
        pass
