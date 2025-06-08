from qdrant_client import AsyncQdrantClient

from .embedding_seeder import EmbeddingSeeder


class MathExpressionDescriptionSeeder(EmbeddingSeeder):  # TODO EmbeddingSeeder[...]
    def __init__(self, client: AsyncQdrantClient):
        super.__init__(client)
