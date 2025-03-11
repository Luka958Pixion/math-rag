from uuid import UUID

from pymongo import AsyncMongoClient, UpdateOne

from math_rag.core.models import MathExpression
from math_rag.infrastructure.mappings.documents import MathExpressionMapping
from math_rag.infrastructure.models.documents import MathExpressionDocument

from .document_repository import DocumentRepository


class MathExpressionRepository(
    DocumentRepository[MathExpression, MathExpressionDocument, MathExpressionMapping]
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)

    async def update_katex(self, id: UUID, katex: str):
        await self.collection.update_one({'_id': id}, {'$set': {'katex': katex}})

    async def batch_update_katex(self, updates: list[tuple[UUID, str]]):
        operations = [
            UpdateOne({'_id': id}, {'$set': {'katex': katex}}) for id, katex in updates
        ]
        await self.collection.bulk_write(operations)
