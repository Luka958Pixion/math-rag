from core.base import EmbeddingRepository
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams


class QdrantRepository(EmbeddingRepository):
    def __init__(self):
        self.client = QdrantClient(host='localhost', port=6333)

    def create_collection(self, name: str) -> bool:
        return self.client.create_collection(
            collection_name=name,
            vectors_config=VectorParams(size=100, distance=Distance.COSINE),
        )

    def delete_collection(self, name: str) -> bool:
        return self.client.delete_collection(name)
