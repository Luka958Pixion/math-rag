from typing import Any

from math_rag.application.models.inference import EMRequest
from math_rag.infrastructure.base import BaseMapping


class EMRequestMapping(BaseMapping[EMRequest, dict[str, Any]]):
    @staticmethod
    def to_source(target: dict[str, Any], **kwargs) -> EMRequest:
        request_id = kwargs['request_id']

        return EMRequest(
            id=request_id,
            text=target['text'],
            params=...,  # TODO mapping
        )

    @staticmethod
    def to_target(source: EMRequest) -> dict[str, Any]:
        # TODO
        return {'encoding_format': 'float'}
