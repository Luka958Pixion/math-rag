from pymongo import AsyncMongoClient

from math_rag.core.models import MathExpressionPrediction


class MathExpressionPredictionRepository:
    def __init__(self, client: AsyncMongoClient, deployment: str):
        self.client = client
        self.db = self.client[deployment]
        self.collection_name = MathExpressionPrediction.__name__.lower()
        self.collection = self.db[self.collection_name]

    async def insert_math_expression_predictions(
        self, items: list[MathExpressionPrediction]
    ):
        item_dicts = [item.model_dump() for item in items]

        for item_dict in item_dicts:
            item_dict['_id'] = item_dict.pop('id')

        await self.collection.insert_many(item_dicts)
