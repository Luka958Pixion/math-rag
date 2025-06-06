from typing import Generic, Protocol, TypeVar

from math_rag.application.base.inference import BaseManagedEM
from math_rag.application.base.repositories.embeddings import BaseEmbeddingRepository
from math_rag.application.base.services import BaseEmbeddingService
from math_rag.application.models.inference import EMConcurrentRequest, EMParams, EMRequest


class GetTextProtocol(Protocol):
    def get_text(self) -> str:
        pass


T = TypeVar('T', bound=GetTextProtocol)


class EmbeddingService(BaseEmbeddingService, Generic[T]):
    def __init__(self, em: BaseManagedEM, embedding_repository: BaseEmbeddingRepository):
        self.em = em
        self.embedding_repository = embedding_repository

    async def index(self, items: list[T]):
        request = EMConcurrentRequest(
            requests=[
                EMRequest(text=item.get_text(), params=EMParams(model=..., dimensions=...))
                for item in items
            ]
        )
        result = await self.em.concurrent_embed(request)
        embeddings = [response.embedding for response in result.response_lists[0].responses]

        await self.embedding_repository.upsert_many(items, embeddings)

    async def search(self, query: str, *, limit: int) -> list[T]:
        request = EMRequest(text=query, params=EMParams(model=..., dimensions=...))
        result = await self.em.embed(request)
        embedding = result.embedding

        return await self.embedding_repository.search(embedding, limit=limit)
