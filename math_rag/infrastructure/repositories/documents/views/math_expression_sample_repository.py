from collections.abc import AsyncGenerator

from bson.binary import UuidRepresentation
from bson.json_util import JSONOptions, dumps, loads
from pymongo import ASCENDING, AsyncMongoClient
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.operations import IndexModel

from math_rag.application.base.repositories.documents.views import (
    BaseMathExpressionSampleRepository,
)
from math_rag.application.models.datasets import MathExpressionSample
from math_rag.core.models import MathExpression, MathExpressionLabel
from math_rag.infrastructure.base import BaseDocumentView
from math_rag.infrastructure.mappings.documents import MathExpressionMapping
from math_rag.infrastructure.models.documents import (
    MathExpressionDocument,
    MathExpressionLabelDocument,
)
from math_rag.infrastructure.models.documents.views import (
    MathExpressionSampleDocumentView,
)


class MathExpressionSampleRepository(BaseMathExpressionSampleRepository):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        self.client = client
        self.db = self.client[deployment]
        self.math_expression_collection_name = MathExpression.__class__.__name__.lower()
        self.math_expression_collection = self.db[self.math_expression_collection_name]
        self.math_expression_label_collection_name = (
            MathExpressionLabel.__class__.__name__.lower()
        )
        self.math_expression_label_collection = self.db[
            self.math_expression_label_collection_name
        ]
        self.json_options = JSONOptions(uuid_representation=UuidRepresentation.STANDARD)

        # TODO seeder for a view

    async def _create_index(
        self,
        collection: AsyncCollection,
        *,
        field: str,
        type: type[BaseDocumentView],
    ):
        if field not in type.model_fields:
            raise ValueError(
                f'Document view {type.__name__} ' f'does not have field {field}'
            )

        index_models = [IndexModel([(field, ASCENDING)], background=True)]
        await collection.create_indexes(index_models)

    async def find_many(self) -> list[MathExpressionSample]:
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
        # TODO
        pass

    async def batch_find_many(
        self, *, batch_size: int
    ) -> AsyncGenerator[list[MathExpressionSample], None]:
        # TODO
        yield
