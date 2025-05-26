from typing import Any

from math_rag.application.enums.inference import LLMErrorRetryPolicy
from math_rag.application.models.inference import LLMError
from math_rag.infrastructure.base import BaseMapping


class LLMErrorMapping(BaseMapping[LLMError, dict[str, Any]]):
    @staticmethod
    def to_source(target: dict[str, Any]) -> LLMError:
        return LLMError(
            message=target['message'] if 'message' in target else str(),
            code=target['code'] if 'code' in target else None,
            body=target['body'] if 'body' in target else None,
            retry_policy=LLMErrorRetryPolicy.NO_RETRY,  # NOTE: NO_RETRY by default
        )

    @staticmethod
    def to_target(source: LLMError) -> dict[str, Any]:
        raise NotImplementedError()
