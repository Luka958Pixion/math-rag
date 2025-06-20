from collections.abc import AsyncGenerator
from datetime import datetime
from uuid import UUID, uuid4

from pymongo import AsyncMongoClient, InsertOne

from math_rag.application.base.repositories.documents import BaseMathExpressionSampleRepository
from math_rag.core.models import MathExpressionSample
from math_rag.infrastructure.mappings.documents import MathExpressionSampleMapping
from math_rag.infrastructure.models.documents import (
    MathExpressionDocument,
    MathExpressionLabelDocument,
    MathExpressionSampleDocument,
)
from math_rag.shared.utils import StrUtil

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

        self.math_expression_collection_name = StrUtil.to_snake_case(
            MathExpressionDocument.__name__
        )
        self.math_expression_collection = self.db[self.math_expression_collection_name]
        self.math_expression_label_collection_name = StrUtil.to_snake_case(
            MathExpressionLabelDocument.__name__
        )
        self.math_expression_label_collection = self.db[self.math_expression_label_collection_name]

    async def _aggregate(
        self, math_expression_dataset_id: UUID
    ) -> AsyncGenerator[MathExpressionSampleProjection, None]:
        match_stage = {
            '$match': {
                'math_expression_dataset_id': math_expression_dataset_id,
                'katex': {'$ne': None},
            }
        }
        lookup_stage = {
            '$lookup': {
                'from': self.math_expression_label_collection_name,
                'localField': '_id',
                'foreignField': 'math_expression_id',
                'as': 'label_doc',
            }
        }
        unwind_stage = {'$unwind': {'path': '$label_doc', 'preserveNullAndEmptyArrays': False}}
        project_stage = {
            '$project': {
                '_id': 0,
                'katex': 1,
                'math_expression_id': '$_id',
                'label': '$label_doc.value',
            }
        }
        pipeline = [match_stage, lookup_stage, unwind_stage, project_stage]

        cursor = await self.math_expression_collection.aggregate(pipeline)

        async for bson_doc in cursor:
            yield MathExpressionSampleProjection.model_validate(bson_doc)

    async def aggregate_and_batch_insert_many(
        self, math_expression_dataset_id: UUID, *, batch_size: int
    ):
        operations = []

        async for projection in self._aggregate(math_expression_dataset_id):
            doc = MathExpressionSampleDocument(
                id=uuid4(),
                math_expression_id=projection.math_expression_id,
                math_expression_dataset_id=math_expression_dataset_id,
                timestamp=datetime.now(),
                katex=projection.katex,
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
