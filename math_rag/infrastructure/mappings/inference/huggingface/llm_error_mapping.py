from typing import Any

from math_rag.application.models.inference import LLMError
from math_rag.infrastructure.base import BaseMapping


class LLMErrorMapping(BaseMapping[LLMError, dict[str, Any]]):
    @staticmethod
    def to_source(target: dict[str, Any]) -> LLMError:
        return LLMError(
            message=str(target['message']),
            body=None,
        )

    @staticmethod
    def to_target(source: LLMError) -> dict[str, Any]:
        raise NotImplementedError()
