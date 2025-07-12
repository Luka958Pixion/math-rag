from pymongo import AsyncMongoClient

from math_rag.application.base.repositories.documents import BaseMathArticleChunkRepository
from math_rag.core.models import MathArticleChunk
from math_rag.infrastructure.mappings.documents import MathArticleChunkMapping
from math_rag.infrastructure.models.documents import MathArticleChunkDocument

from .document_repository import DocumentRepository


class MathArticleChunkRepository(
    BaseMathArticleChunkRepository,
    DocumentRepository[MathArticleChunk, MathArticleChunkDocument, MathArticleChunkMapping],
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
