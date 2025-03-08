from uuid import UUID

from pymongo import AsyncMongoClient, InsertOne, UpdateOne

from math_rag.application.base.repositories.documents import (
    BaseMathExpressionRepository,
)
from math_rag.core.models import MathExpression
from math_rag.infrastructure.models.documents import MathExpressionDocument


class MathExpressionRepository(BaseMathExpressionRepository):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        self.client = client
        self.db = self.client[deployment]
        self.collection_name = MathExpression.__name__.lower()
        self.collection = self.db[self.collection_name]

    async def insert_math_expressions(self, items: list[MathExpression]):
        docs = [MathExpressionDocument.from_internal(item) for item in items]
        bson_docs = [doc.model_dump() for doc in docs]

        await self.collection.insert_many(bson_docs)

    async def batch_insert_math_expressions(
        self, items: list[MathExpression], batch_size: int
    ):
        operations = []

        for item in items:
            doc = MathExpressionDocument.from_internal(item)
            bson_doc = doc.model_dump()
            operations.append(InsertOne(bson_doc))

        for i in range(0, len(operations), batch_size):
            batch = operations[i : i + batch_size]
            await self.collection.bulk_write(batch)

    async def get_math_expression_by_id(self, id: UUID) -> MathExpression | None:
        bson_doc = await self.collection.find_one({'_id': id})

        if bson_doc:
            doc = MathExpressionDocument(**bson_doc)
            item = MathExpressionDocument.to_internal(doc)

            return item

        return None

    async def get_math_expressions(
        self, limit: int | None = None
    ) -> list[MathExpression]:
        cursor = self.collection.find()

        if limit:
            cursor = cursor.limit(limit)

        bson_docs = await cursor.to_list(length=limit)
        docs = [MathExpressionDocument(**bson_doc) for bson_doc in bson_docs]
        items = [MathExpressionDocument.to_internal(doc) for doc in docs]

        return items

    async def update_katex(self, id: UUID, katex: str):
        await self.collection.update_one({'_id': id}, {'$set': {'katex': katex}})

    async def batch_update_katex(self, updates: list[tuple[UUID, str]]):
        operations = [
            UpdateOne({'_id': id}, {'$set': {'katex': katex}}) for id, katex in updates
        ]
        await self.collection.bulk_write(operations)
