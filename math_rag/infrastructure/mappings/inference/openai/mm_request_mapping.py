from typing import Any

from math_rag.application.models.inference import MMParams, MMRequest
from math_rag.infrastructure.base import BaseMapping


class MMRequestMapping(BaseMapping[MMRequest, dict[str, Any]]):
    @staticmethod
    def to_source(target: dict[str, Any], **kwargs) -> MMRequest:
        request_id = kwargs['request_id']

        return MMRequest(
            id=request_id,
            text=target['input'],
            params=MMParams(model=target['model']),
            router_params=None,
        )

    @staticmethod
    def to_target(source: MMRequest) -> dict[str, Any]:
        return {
            'input': source.text,
            'model': source.params.model,
        }
