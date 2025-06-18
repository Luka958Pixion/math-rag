from abc import ABC, abstractmethod

from math_rag.application.models import KatexRenderResult, KatexRenderSvgResult, KatexValidateResult


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
    async def render_svg(self, katex: str) -> KatexRenderSvgResult:
        pass

    @abstractmethod
    async def render_svg_many(self, katexes: list[str]) -> list[KatexRenderSvgResult]:
        pass

    @abstractmethod
    async def batch_render_svg_many(
        self, katexes: list[str], *, batch_size: int
    ) -> list[KatexRenderSvgResult]:
        pass

    @abstractmethod
    async def batch_render_many(
        self, katexes: list[str], *, batch_size: int
    ) -> list[KatexRenderResult]:
        pass
