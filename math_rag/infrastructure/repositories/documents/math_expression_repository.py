from uuid import UUID

from pymongo import AsyncMongoClient

from math_rag.application.base.repositories.documents import (
    BaseMathExpressionRepository,
)
from math_rag.core.models import MathExpression


class MathExpressionRepository(BaseMathExpressionRepository):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        self.client = client
        self.db = self.client[deployment]
        self.collection_name = MathExpression.__name__.lower()
        self.collection = self.db[self.collection_name]

    async def insert_math_expressions(self, items: list[MathExpression]):
        item_dicts = [item.model_dump() for item in items]

        for item_dict in item_dicts:
            item_dict['_id'] = item_dict.pop('id')

        await self.collection.insert_many(item_dicts)

    async def batch_insert_math_expressions(
        self, items: list[MathExpression], batch_size: int
    ):
        for i in range(0, len(items), batch_size):
            items_batch = items[i : i + batch_size]
            await self.insert_math_expressions(items_batch)

    async def get_math_expression_by_id(self, id: UUID) -> MathExpression | None:
        doc = await self.collection.find_one({'_id': id})

        if doc:
            return MathExpression(**doc)

        return None

    async def get_math_expressions(
        self, limit: int | None = None
    ) -> list[MathExpression]:
        cursor = self.collection.find()

        if limit:
            cursor = cursor.limit(limit)

        docs = await cursor.to_list(length=limit)

        for doc in docs:
            doc['id'] = doc.pop('_id')

        return [MathExpression(**doc) for doc in docs]
