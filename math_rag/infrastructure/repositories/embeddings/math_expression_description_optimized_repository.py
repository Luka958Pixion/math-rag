from qdrant_client import AsyncQdrantClient

from math_rag.application.base.repositories.embeddings import (
    BaseMathExpressionDescriptionOptimizedRepository,
)
from math_rag.core.models import MathExpressionDescriptionOptimized
from math_rag.infrastructure.mappings.embeddings import MathExpressionDescriptionOptimizedMapping
from math_rag.infrastructure.models.embeddings import (
    MathExpressionDescriptionOptimizedEmbedding,
)

from .embedding_repository import EmbeddingRepository


class MathExpressionDescriptionOptimizedRepository(
    BaseMathExpressionDescriptionOptimizedRepository,
    EmbeddingRepository[
        MathExpressionDescriptionOptimized,
        MathExpressionDescriptionOptimizedEmbedding,
        MathExpressionDescriptionOptimizedMapping,
    ],
):
    def __init__(self, client: AsyncQdrantClient):
        super().__init__(client)
