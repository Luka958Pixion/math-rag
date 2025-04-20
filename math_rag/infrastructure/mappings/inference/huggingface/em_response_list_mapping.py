from math_rag.application.models.inference import EMResponseList
from math_rag.infrastructure.base import BaseMapping

from .em_response_mapping import EMResponseMapping


class EMResponseListMapping(BaseMapping[EMResponseList, list[float]]):
    @staticmethod
    def to_source(target: list[float], **kwargs) -> EMResponseList:
        request_id = kwargs['request_id']

        return EMResponseList(
            request_id=request_id,
            responses=[EMResponseMapping.to_source(target)],
        )

    @staticmethod
    def to_target(source: EMResponseList) -> list[float]:
        raise NotImplementedError()
