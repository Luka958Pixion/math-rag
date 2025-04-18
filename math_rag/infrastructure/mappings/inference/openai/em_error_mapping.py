from typing import Any

from math_rag.application.models.inference import EMError
from math_rag.infrastructure.base import BaseMapping


class EMErrorMapping(BaseMapping[EMError, dict[str, Any]]):
    @staticmethod
    def to_source(target: dict[str, Any]) -> EMError:
        return EMError(
            message=target['message'] if 'message' in target else str(),
            body=target['body'] if 'body' in target else None,
        )

    @staticmethod
    def to_target(source: EMError) -> dict[str, Any]:
        raise NotImplementedError()
