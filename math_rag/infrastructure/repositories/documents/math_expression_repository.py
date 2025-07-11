from uuid import UUID

from pymongo import AsyncMongoClient

from math_rag.application.base.repositories.documents import BaseMathExpressionRepository
from math_rag.core.models import MathExpression
from math_rag.infrastructure.mappings.documents import MathExpressionMapping
from math_rag.infrastructure.models.documents import MathExpressionDocument

from .document_repository import DocumentRepository


class MathExpressionRepository(
    BaseMathExpressionRepository,
    DocumentRepository[MathExpression, MathExpressionDocument, MathExpressionMapping],
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)

    async def update_group_id(self, ids: list[UUID], group_id: UUID):
        await self.update_many(
            filter={'id': {'$in': ids}},
            update={'math_expression_group_id': group_id},
        )
