import asyncio

from pathlib import Path
from uuid import UUID

from minio import Minio

from math_rag.application.base.repositories.objects import BaseMathArticleRepository
from math_rag.core.models import MathArticle
from math_rag.infrastructure.mappings.objects import MathArticleMapping
from math_rag.infrastructure.models.documents import ObjectMetadataDocument
from math_rag.infrastructure.models.objects import MathArticleObject
from math_rag.infrastructure.repositories.documents import ObjectMetadataRepository

from .object_repository import ObjectRepository


BACKUP_PATH = Path('../../../../.tmp/backups/minio')


class MathArticleRepository(
    BaseMathArticleRepository,
    ObjectRepository[MathArticle, MathArticleObject, MathArticleMapping],
):
    def __init__(self, client: Minio, object_metadata_repository: ObjectMetadataRepository):
        metadata_keys = [
            'id',
            'math_expression_dataset_id',
            'math_expression_index_id',
            'timestamp',
        ]

        for key in metadata_keys:
            if key not in MathArticle.model_fields:
                raise ValueError(f'Field {key} does not exist in {MathArticle.__class__.__name__}')

        super().__init__(client, metadata_keys, object_metadata_repository)

    async def find_by_id(self, id: UUID) -> MathArticle | None:
        doc = await self.object_metadata_repository.find_one(filter={'metadata.id': str(id)})

        if not doc:
            return None

        return self.find_by_name(doc.object_name)

    async def find_by_math_expression_index_id(self, id: UUID) -> MathArticle | None:
        doc = await self.object_metadata_repository.find_one(
            filter={'metadata.math_expression_index_id': str(id)}
        )

        if not doc:
            return None

        return self.find_by_name(doc.object_name)

    async def find_many_by_math_expression_index_id(self, id: UUID) -> list[MathArticle]:
        docs = await self.object_metadata_repository.find_many(
            filter={'metadata.math_expression_index_id': str(id)}
        )

        if not docs:
            return []

        return [self.find_by_name(doc.object_name) for doc in docs]

    async def find_many_by_math_expression_dataset_id(self, id: UUID) -> list[MathArticle]:
        docs = await self.object_metadata_repository.find_many(
            filter={'metadata.math_expression_dataset_id': str(id)}
        )

        if not docs:
            return []

        return [self.find_by_name(doc.object_name) for doc in docs]
