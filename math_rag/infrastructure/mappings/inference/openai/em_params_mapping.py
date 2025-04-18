from typing import Any

from math_rag.application.models.inference import EMParams
from math_rag.infrastructure.base import BaseMapping


class EMParamsMapping(BaseMapping[EMParams, dict[str, Any]]):
    @staticmethod
    def to_source(target: dict[str, Any], **kwargs) -> EMParams:
        request_id = kwargs['request_id']  # TODO not request id

        return EMParams(
            id=request_id,
            model=target['model'],
        )

    @staticmethod
    def to_target(source: EMParams) -> dict[str, Any]:
        # TODO
        return {}
