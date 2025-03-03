from abc import ABC, abstractmethod

from math_rag.application.models import KatexValidationResult


class BaseKatexValidationService(ABC):
    @abstractmethod
    def validate(self, katex: str) -> KatexValidationResult:
        pass

    @abstractmethod
    def validate_many(self, katexes: list[str]) -> list[KatexValidationResult]:
        pass
