from uuid import UUID

from pymongo import AsyncMongoClient

from math_rag.application.base.repositories.documents import BaseIndexRepository
from math_rag.core.enums import IndexBuildStage, IndexBuildStatus
from math_rag.core.models import Index
from math_rag.infrastructure.mappings.documents import IndexMapping
from math_rag.infrastructure.models.documents import IndexDocument

from .document_repository import DocumentRepository


class IndexRepository(
    BaseIndexRepository,
    DocumentRepository[Index, IndexDocument, IndexMapping],
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)

    async def update_build_stage(
        self, id: UUID, index_build_stage: IndexBuildStage
    ) -> Index:
        await self.collection.update_one(
            {'_id': id}, {'$set': {'index_build_stage': index_build_stage.value}}
        )

    async def update_build_status(
        self, id: UUID, index_build_status: IndexBuildStatus
    ) -> Index:
        await self.collection.update_one(
            {'_id': id}, {'$set': {'index_build_status': index_build_status.value}}
        )
