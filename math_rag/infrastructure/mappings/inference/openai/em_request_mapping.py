from typing import Any

from math_rag.application.models.inference import EMParams, EMRequest
from math_rag.infrastructure.base import BaseMapping


class EMRequestMapping(BaseMapping[EMRequest, dict[str, Any]]):
    @staticmethod
    def to_source(target: dict[str, Any], **kwargs) -> EMRequest:
        request_id = kwargs['request_id']

        return EMRequest(
            id=request_id, text=target['input'], params=EMParams(model=target['model'])
        )

    @staticmethod
    def to_target(source: EMRequest) -> dict[str, Any]:
        return {
            'input': source.text,
            'model': source.params.model,
            'encoding_format': 'float',
        }
