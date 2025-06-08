from qdrant_client import AsyncQdrantClient

from math_rag.application.base.repositories.embeddings import (
    BaseMathExpressionDescriptionRepository,
)
from math_rag.core.models import MathExpressionDescription
from math_rag.infrastructure.mappings.embeddings import MathExpressionDescriptionMapping
from math_rag.infrastructure.models.embeddings import MathExpressionDescriptionEmbedding

from .embedding_repository import EmbeddingRepository


class MathExpressionDescriptionRepository(
    BaseMathExpressionDescriptionRepository,
    EmbeddingRepository[
        MathExpressionDescription,
        MathExpressionDescriptionEmbedding,
        MathExpressionDescriptionMapping,
    ],
):
    def __init__(self, client: AsyncQdrantClient):
        super().__init__(client)
