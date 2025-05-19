from typing import Generic

from math_rag.application.models.inference import LLMFailedRequest
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import LLMFailedRequestDocument

from .llm_error_mapping import LLMErrorMapping
from .llm_request_mapping import LLMRequestMapping


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
            errors=[LLMErrorMapping.to_target(error) for error in source.errors],
        )
