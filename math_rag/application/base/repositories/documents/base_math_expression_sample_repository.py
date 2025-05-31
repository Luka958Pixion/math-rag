from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from uuid import UUID

from math_rag.core.models import MathExpressionSample


class BaseMathExpressionSampleRepository(ABC):
    @abstractmethod
    async def aggregate_and_batch_insert_many(
        self, math_expression_dataset_id: UUID, *, batch_size: int
    ):
        pass

    @abstractmethod
    async def batch_find_many(
        self, math_expression_dataset_id: UUID, *, batch_size: int
    ) -> AsyncGenerator[list[MathExpressionSample], None]:
        pass
