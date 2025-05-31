from collections.abc import AsyncGenerator
from datetime import datetime
from uuid import UUID, uuid4

from pymongo import ASCENDING, AsyncMongoClient, InsertOne

from math_rag.application.base.repositories.documents import BaseMathExpressionSampleRepository
from math_rag.core.models import MathExpression, MathExpressionLabel, MathExpressionSample
from math_rag.infrastructure.mappings.documents import MathExpressionSampleMapping
from math_rag.infrastructure.models.documents import MathExpressionSampleDocument

from .document_repository import DocumentRepository
from .projections.math_expression_sample_projection import MathExpressionSampleProjection


class MathExpressionSampleRepository(
    BaseMathExpressionSampleRepository,
    DocumentRepository[
        MathExpressionSample, MathExpressionSampleDocument, MathExpressionSampleMapping
    ],
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)

        self.math_expression_collection_name = MathExpression.__class__.__name__.lower()
        self.math_expression_collection = self.db[self.math_expression_collection_name]
        self.math_expression_label_collection_name = MathExpressionLabel.__class__.__name__.lower()
        self.math_expression_label_collection = self.db[self.math_expression_label_collection_name]

    async def _aggregate(
        self, math_expression_dataset_id: UUID
    ) -> AsyncGenerator[MathExpressionSampleProjection, None]:
        match_stage = {'$match': {'math_expression_dataset_id': math_expression_dataset_id}}
        lookup_stage = {
            '$lookup': {
                'from': self.math_expression_label_collection_name,
                'let': {'exprId': '$_id', 'datasetId': '$math_expression_dataset_id'},
                'pipeline': [
                    {
                        '$match': {
                            '$expr': {
                                '$and': [
                                    {'$eq': ['$math_expression_id', '$$exprId']},
                                    {'$eq': ['$math_expression_dataset_id', '$$datasetId']},
                                ]
                            }
                        }
                    },
                    {'$project': {'_id': 0, 'label': 1}},
                    {'$limit': 1},
                ],
                'as': 'label_doc',
            }
        }
        unwind_stage = {'$unwind': {'path': '$label_doc', 'preserveNullAndEmptyArrays': False}}
        project_stage = {'$project': {'_id': 0, 'latex': 1, 'label': '$label_doc.label'}}
        pipeline = [match_stage, lookup_stage, unwind_stage, project_stage]

        cursor = await self.math_expression_collection.aggregate(
            pipeline,
            jsonOptions=self.json_options,
        )

        async for bson_doc in cursor:
            yield MathExpressionSampleProjection.model_validate(bson_doc)

    async def aggregate_and_batch_insert_many(
        self, math_expression_dataset_id: UUID, *, batch_size: int
    ):
        operations = []

        async for projection in self._aggregate(math_expression_dataset_id):
            doc = MathExpressionSampleDocument(
                id=uuid4(),
                math_expression_dataset_id=math_expression_dataset_id,
                timestamp=datetime.now(),
                latex=projection.latex,
                label=projection.label,
            )
            bson_doc = doc.model_dump()
            operations.append(InsertOne(bson_doc))

        for i in range(0, len(operations), batch_size):
            batch = operations[i : i + batch_size]
            await self.collection.bulk_write(batch)

    async def batch_find_many(
        self, math_expression_dataset_id: UUID, *, batch_size: int
    ) -> AsyncGenerator[list[MathExpressionSample], None]:
        async for batch in DocumentRepository[
            MathExpressionSample, MathExpressionSampleDocument, MathExpressionSampleMapping
        ].batch_find_many(
            self,
            batch_size=batch_size,
            filter={'math_expression_dataset_id': math_expression_dataset_id},
        ):
            yield batch
