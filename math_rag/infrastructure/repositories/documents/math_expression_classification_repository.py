from pymongo import AsyncMongoClient

from math_rag.core.models import MathExpressionClassification
from math_rag.infrastructure.models.documents import (
    MathExpressionClassificationDocument,
)


class MathExpressionClassificationRepository:
    def __init__(self, client: AsyncMongoClient, deployment: str):
        self.client = client
        self.db = self.client[deployment]
        self.collection_name = MathExpressionClassification.__name__.lower()
        self.collection = self.db[self.collection_name]

    async def insert_math_expression_classifications(
        self, items: list[MathExpressionClassification]
    ):
        docs = [
            MathExpressionClassificationDocument.from_internal(item) for item in items
        ]
        bson_docs = [doc.model_dump() for doc in docs]

        await self.collection.insert_many(bson_docs)

    async def get_math_expression_classifications(
        self, limit: int
    ) -> list[MathExpressionClassification]:
        cursor = self.collection.find().limit(limit)
        bson_docs = await cursor.to_list(length=limit)
        docs = [
            MathExpressionClassificationDocument(**bson_doc) for bson_doc in bson_docs
        ]
        items = [MathExpressionClassificationDocument.to_internal(doc) for doc in docs]

        return items
