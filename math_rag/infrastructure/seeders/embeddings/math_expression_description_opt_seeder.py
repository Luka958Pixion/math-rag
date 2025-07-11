from qdrant_client import AsyncQdrantClient

from math_rag.infrastructure.models.embeddings import (
    MathExpressionDescriptionOptEmbedding,
)

from .embedding_seeder import EmbeddingSeeder


class MathExpressionDescriptionOptSeeder(EmbeddingSeeder[MathExpressionDescriptionOptEmbedding]):
    def __init__(self, client: AsyncQdrantClient):
        super().__init__(client)
