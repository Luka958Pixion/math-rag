from math_rag.application.models.inference import LLMFailedRequest
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import LLMFailedRequestDocument


class LLMFailedRequestMapping(BaseMapping[LLMFailedRequest, LLMFailedRequestDocument]):
    @staticmethod
    def to_source(target: LLMFailedRequestDocument) -> LLMFailedRequest:
        # TODO
        source = LLMFailedRequest(
            id=target._id, request=target.request, errors=target.errors
        )

        return source

    @staticmethod
    def to_target(source: LLMFailedRequest) -> LLMFailedRequestDocument:
        target = LLMFailedRequestDocument(
            _id=source.id,
            _type=source.__class__.__name__,
            request=source.request,
            errors=source.errors,
        )

        return target
