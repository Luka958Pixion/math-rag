from uuid import UUID

from pymongo import AsyncMongoClient

from math_rag.application.base.repositories.documents import (
    BaseMathExpressionRepository,
)
from math_rag.core.enums import MathCategory
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

    async def get_math_expression_by_id(self, id: UUID) -> MathExpression | None:
        doc = await self.collection.find_one({'_id': id})

        if doc:
            return MathExpression(**doc)

        return None

    async def get_math_expressions_by_category(
        self, limit: int
    ) -> list[MathExpression]:
        pipeline = [
            {'$sort': {'position': 0}},
            {'$group': {'_id': '$math_category', 'expressions': {'$push': '$$ROOT'}}},
            {'$project': {'expressions': {'$slice': ['$expressions', limit]}}},
        ]

        cursor = await self.collection.aggregate(pipeline)
        results = []

        async for item in cursor:
            for expr in item['expressions']:
                expr['id'] = expr.pop('_id')

                results.append(MathExpression(**expr))

        return results
