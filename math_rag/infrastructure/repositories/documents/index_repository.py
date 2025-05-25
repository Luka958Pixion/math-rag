from uuid import UUID

from pymongo import AsyncMongoClient, ReturnDocument

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
        bson_doc = await self.collection.find_one_and_update(
            filter={'_id': id},
            update={'$set': {'index_build_stage': index_build_stage.value}},
            return_document=ReturnDocument.AFTER,
        )
        doc = self.target_cls.model_validate(bson_doc)

        return self.mapping_cls.to_source(doc)

    async def update_build_status(
        self, id: UUID, index_build_status: IndexBuildStatus
    ) -> Index:
        bson_doc = await self.collection.find_one_and_update(
            filter={'_id': id},
            update={'$set': {'index_build_status': index_build_status.value}},
            return_document=ReturnDocument.AFTER,
        )
        doc = self.target_cls.model_validate(bson_doc)

        return self.mapping_cls.to_source(doc)
