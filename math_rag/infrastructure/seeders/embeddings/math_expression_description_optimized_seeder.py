from qdrant_client import AsyncQdrantClient

from math_rag.infrastructure.models.embeddings import (
    MathExpressionDescriptionOptimizedEmbedding,
)

from .embedding_seeder import EmbeddingSeeder


class MathExpressionDescriptionOptimizedSeeder(
    EmbeddingSeeder[MathExpressionDescriptionOptimizedEmbedding]
):
    def __init__(self, client: AsyncQdrantClient):
        super().__init__(client)
