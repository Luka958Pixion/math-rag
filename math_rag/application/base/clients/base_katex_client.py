from abc import ABC, abstractmethod

from math_rag.application.models import KatexRenderResult, KatexValidateResult


class BaseKatexClient(ABC):
    @abstractmethod
    async def validate(self, katex: str) -> KatexValidateResult:
        pass

    @abstractmethod
    async def validate_many(self, katexes: list[str]) -> list[KatexValidateResult]:
        pass

    @abstractmethod
    async def batch_validate_many(
        self, katexes: list[str], *, batch_size: int
    ) -> list[KatexValidateResult]:
        pass

    @abstractmethod
    async def health(self) -> bool:
        pass

    @abstractmethod
    async def render(self, katex: str) -> KatexRenderResult:
        pass

    @abstractmethod
    async def render_many(self, katexes: list[str]) -> list[KatexRenderResult]:
        pass

    @abstractmethod
    async def batch_render_many(
        self, katexes: list[str], *, batch_size: int
    ) -> list[KatexRenderResult]:
        pass
