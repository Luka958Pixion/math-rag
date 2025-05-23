from uuid import UUID

from pymongo import AsyncMongoClient

from math_rag.application.base.repositories.documents import BaseIndexRepository
from math_rag.core.enums import IndexBuildStatus
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

    async def update_build_status(
        index_id: UUID, index_build_status: IndexBuildStatus
    ) -> Index:
        # TODO
        pass
