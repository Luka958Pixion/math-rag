from collections import defaultdict

from pymongo import AsyncMongoClient

from math_rag.application.base.repositories.documents import (
    MathExpressionBaseRepository,
)
from math_rag.core.enums import MathCategory
from math_rag.core.models import MathExpression


class MathExpressionRepository(MathExpressionBaseRepository):
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

    async def get_math_expressions_by_category(
        self, limit: int
    ) -> dict[MathCategory, list[MathExpression]]:
        pipeline = [
            {'$sort': {'position': 1}},
            {'$group': {'_id': '$math_category', 'expressions': {'$push': '$$ROOT'}}},
            {'$project': {'expressions': {'$slice': ['$expressions', limit]}}},
        ]

        cursor = await self.collection.aggregate(pipeline)
        result = {}

        async for item in cursor:
            math_category_value = item['_id']
            expressions = item['expressions']

            for expr in expressions:
                if '_id' in expr:
                    expr['id'] = expr.pop('_id')

            result[MathCategory(math_category_value)] = [
                MathExpression(**expr) for expr in expressions
            ]

        for category in MathCategory:
            if category not in result:
                result[category] = []

        return result
