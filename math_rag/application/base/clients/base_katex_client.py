from abc import ABC, abstractmethod

from math_rag.application.models import KatexValidationResult


class BaseKatexClient(ABC):
    @abstractmethod
    async def validate(self, katex: str) -> KatexValidationResult:
        pass

    @abstractmethod
    async def validate_many(self, katexes: list[str]) -> list[KatexValidationResult]:
        pass

    @abstractmethod
    async def batch_validate_many(
        self, katexes: list[str], *, batch_size: int
    ) -> list[KatexValidationResult]:
        pass

    @abstractmethod
    async def health(self) -> bool:
        pass
