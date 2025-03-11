from typing import Generic

from math_rag.application.models.inference import LLMFailedRequest
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.mappings.documents import LLMRequestMapping
from math_rag.infrastructure.models.documents import LLMFailedRequestDocument


class LLMFailedRequestMapping(
    BaseMapping[LLMFailedRequest[LLMResponseType], LLMFailedRequestDocument],
    Generic[LLMResponseType],
):
    @staticmethod
    def to_source(target: LLMFailedRequestDocument) -> LLMFailedRequest:
        return LLMFailedRequest(
            id=target.id,
            request=LLMRequestMapping[LLMResponseType].to_source(target.request),
            errors=target.errors,
        )

    @staticmethod
    def to_target(source: LLMFailedRequest) -> LLMFailedRequestDocument:
        return LLMFailedRequestDocument(
            id=source.id,
            request=LLMRequestMapping[LLMResponseType].to_target(source.request),
            errors=source.errors,
        )
