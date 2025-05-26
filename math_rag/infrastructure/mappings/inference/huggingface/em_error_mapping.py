from typing import Any

from math_rag.application.enums.inference import EMErrorRetryPolicy
from math_rag.application.models.inference import EMError
from math_rag.infrastructure.base import BaseMapping


class EMErrorMapping(BaseMapping[EMError, dict[str, Any]]):
    @staticmethod
    def to_source(target: dict[str, Any]) -> EMError:
        return EMError(
            message=str(target['message']),
            code=None,
            body=None,
            retry_policy=EMErrorRetryPolicy.NO_RETRY,  # NOTE: NO_RETRY by default
        )

    @staticmethod
    def to_target(source: EMError) -> dict[str, Any]:
        raise NotImplementedError()
