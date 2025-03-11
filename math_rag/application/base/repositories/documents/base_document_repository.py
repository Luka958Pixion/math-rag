from typing import Generic
from uuid import UUID

from math_rag.infrastructure.types import MappingType, SourceType, TargetType


class BaseDocumentRepository(Generic[SourceType, TargetType, MappingType]):
    async def insert_one(self, item: SourceType):
        pass

    async def insert_many(self, items: list[SourceType]):
        pass

    async def batch_insert_many(self, items: list[SourceType], *, batch_size: int):
        pass

    async def find_by_id(self, id: UUID) -> SourceType | None:
        pass

    async def find_many(self, *, limit: int | None = None) -> list[SourceType]:
        pass
