from qdrant_client import AsyncQdrantClient

from math_rag.infrastructure.models.embeddings import MathExpressionDescriptionEmbedding

from .embedding_seeder import EmbeddingSeeder


class MathExpressionDescriptionSeeder(EmbeddingSeeder[MathExpressionDescriptionEmbedding]):
    def __init__(self, client: AsyncQdrantClient):
        super().__init__(client)
