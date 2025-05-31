from abc import abstractmethod
from collections.abc import AsyncGenerator
from uuid import UUID

from math_rag.core.models import MathExpressionSample

from .base_document_repository import BaseDocumentRepository


class BaseMathExpressionSampleRepository(BaseDocumentRepository[MathExpressionSample]):
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
