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
        metadata_keys = ['id', 'math_expression_dataset_id', 'index_id', 'timestamp']

        for key in metadata_keys:
            if key not in MathArticle.model_fields:
                raise ValueError(f'Field {key} does not exist in {MathArticle.__class__.__name__}')

        super().__init__(client, metadata_keys, object_metadata_repository)

    def find_by_id(self, id: UUID) -> MathArticle | None:
        coro = self.object_metadata_repository.find_one(filter={'metadata.id': str(id)})
        doc: ObjectMetadataDocument | None = asyncio.run(coro)

        if not doc:
            return None

        return self.find_by_name(doc.object_name)

    def find_many_by_index_id(self, id: UUID) -> list[MathArticle]:
        coro = self.object_metadata_repository.find_many(filter={'metadata.index_id': str(id)})
        docs: list[ObjectMetadataDocument] = asyncio.run(coro)

        if not docs:
            return []

        return [self.find_by_name(doc.object_name) for doc in docs]

    def find_many_by_math_expression_dataset_id(self, id: UUID) -> list[MathArticle]:
        coro = self.object_metadata_repository.find_many(
            filter={'metadata.math_expression_dataset_id': str(id)}
        )
        docs: list[ObjectMetadataDocument] = asyncio.run(coro)

        if not docs:
            return []

        return [self.find_by_name(doc.object_name) for doc in docs]
