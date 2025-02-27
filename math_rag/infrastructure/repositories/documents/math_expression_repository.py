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
            {
                '$project': {
                    '_id': 1,
                    'expressions': {'$slice': ['$expressions', limit]},
                }
            },
        ]

        cursor = self.collection.aggregate(pipeline)
        category_map = defaultdict(list)

        async for item in cursor:
            category = MathCategory(item['_id'])
            expressions = [
                MathExpression(**{**expr, 'id': expr.pop('_id')})
                for expr in item['expressions']
            ]
            category_map[category] = expressions

        return category_map
