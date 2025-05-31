from collections.abc import AsyncGenerator

from bson.binary import UuidRepresentation
from bson.json_util import JSONOptions
from pymongo import ASCENDING, AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.command_cursor import AsyncCommandCursor
from pymongo.operations import IndexModel

from math_rag.application.base.repositories.documents import BaseMathExpressionSampleRepository
from math_rag.core.models import MathExpression, MathExpressionLabel, MathExpressionSample
from math_rag.infrastructure.base import BaseDocumentView
from math_rag.infrastructure.mappings.documents.views import MathExpressionSampleMapping
from math_rag.infrastructure.models.documents import (
    MathExpressionDocument,
    MathExpressionLabelDocument,
)


class MathExpressionSampleRepository(BaseMathExpressionSampleRepository):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        self.client = client
        self.db = self.client[deployment]
        self.math_expression_collection_name = MathExpression.__class__.__name__.lower()
        self.math_expression_collection = self.db[self.math_expression_collection_name]
        self.math_expression_label_collection_name = MathExpressionLabel.__class__.__name__.lower()
        self.math_expression_label_collection = self.db[self.math_expression_label_collection_name]
        self.json_options = JSONOptions(uuid_representation=UuidRepresentation.STANDARD)

    async def _create_index(
        self,
        collection: AsyncCollection,
        *,
        field: str,
        type: type[BaseDocumentView],
    ):
        if field not in type.model_fields:
            raise ValueError(f'Document view {type.__name__} does not have field {field}')

        index_models = [IndexModel([(field, ASCENDING)], background=True)]
        await collection.create_indexes(index_models)

    async def _find_many_cursor(self) -> AsyncCommandCursor:
        await self._create_index(
            self.math_expression_collection,
            field='id',
            type=MathExpressionDocument,
        )
        await self._create_index(
            self.math_expression_label_collection,
            field='math_expression_id',
            type=MathExpressionLabelDocument,
        )

        lookup_stage = {
            '$lookup': {
                'from': self.math_expression_label_collection_name,
                'let': {'exprId': '$_id'},
                'pipeline': [
                    {'$match': {'$expr': {'$eq': ['$math_expression_id', '$$exprId']}}},
                    {'$project': {'_id': 0, 'label': 1}},
                    {'$limit': 1},
                ],
                'as': 'label_doc',
            }
        }
        unwind_stage = {'$unwind': {'path': '$label_doc', 'preserveNullAndEmptyArrays': False}}
        project_stage = {
            '$project': {
                '_id': 0,
                'latex': 1,
                'label': '$label_doc.label',
            }
        }
        pipeline = [lookup_stage, unwind_stage, project_stage]

        return await self.math_expression_collection.aggregate(
            pipeline,
            jsonOptions=self.json_options,
        )

    async def find_many(self) -> list[MathExpressionSample]:
        cursor = await self._find_many_cursor()
        bson_docs = await cursor.to_list()

        docs = [MathExpressionSampleDocumentView.model_validate(bson_doc) for bson_doc in bson_docs]
        items = [MathExpressionSampleMapping.to_source(doc) for doc in docs]

        return items

    async def batch_find_many(
        self, *, batch_size: int
    ) -> AsyncGenerator[list[MathExpressionSample], None]:
        cursor = await self._find_many_cursor()

        async for bson_doc in cursor:
            doc = MathExpressionSampleDocumentView.model_validate(bson_doc)
            item = MathExpressionSampleMapping.to_source(doc)
            batch.append(item)

            if len(batch) >= batch_size:
                yield batch
                batch = []

        if batch:
            yield batch
