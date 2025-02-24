from pymongo import AsyncMongoClient

from math_rag.application.base.repositories.documents import (
    MathExpressionBaseRepository,
)
from math_rag.core.models import MathExpression


class MathExpressionRepository(MathExpressionBaseRepository):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        self.client = client
        self.db = self.client[deployment]
        self.collection_name = MathExpression.__name__.lower()

    async def insert_math_expressions(self, items: list[MathExpression]):
        item_dicts = [item.model_dump() for item in items]

        for item_dict in item_dicts:
            item_dict['_id'] = item_dict.pop('id')

        await self.db[self.collection_name].insert_many(item_dicts)
