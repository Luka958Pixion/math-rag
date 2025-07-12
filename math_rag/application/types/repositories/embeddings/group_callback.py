from typing import Protocol
from uuid import UUID


class GroupCallback(Protocol):
    def __call__(self, ids: list[UUID], embeddings: list[list[float]]) -> list[list[UUID]]:
        pass
