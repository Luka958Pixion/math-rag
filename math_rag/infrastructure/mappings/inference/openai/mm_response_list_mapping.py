from math_rag.application.models.inference import MMResponseList
from math_rag.infrastructure.base import BaseMapping
from openai.types import ModerationCreateResponse

from .mm_response_mapping import MMResponseMapping


class MMResponseListMapping(BaseMapping[MMResponseList, ModerationCreateResponse]):
    @staticmethod
    def to_source(target: ModerationCreateResponse, **kwargs) -> MMResponseList:
        request_id = kwargs['request_id']

        return MMResponseList(
            request_id=request_id,
            responses=[MMResponseMapping.to_source(result) for result in target.results],
        )

    @staticmethod
    def to_target(source: MMResponseList) -> ModerationCreateResponse:
        raise NotImplementedError()
