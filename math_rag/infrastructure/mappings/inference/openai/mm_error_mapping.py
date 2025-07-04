from typing import Any

from math_rag.application.enums.inference import MMErrorRetryPolicy
from math_rag.application.models.inference import MMError
from math_rag.infrastructure.base import BaseMapping


class MMErrorMapping(BaseMapping[MMError, dict[str, Any]]):
    @staticmethod
    def to_source(target: dict[str, Any]) -> MMError:
        return MMError(
            message=target['message'] if 'message' in target else str(),
            code=target['code'] if 'code' in target else None,
            body=target['body'] if 'body' in target else None,
            retry_policy=MMErrorRetryPolicy.NO_RETRY,  # NOTE: NO_RETRY by default
        )

    @staticmethod
    def to_target(source: MMError) -> dict[str, Any]:
        raise NotImplementedError()
