from math_rag.application.models.inference import LLMFailedRequest
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import LLMFailedRequestDocument


class LLMFailedRequestMapping(BaseMapping[LLMFailedRequest, LLMFailedRequestDocument]):
    @staticmethod
    def to_source(target: LLMFailedRequestDocument) -> LLMFailedRequest:
        # TODO
        return LLMFailedRequest(
            id=target._id, request=target.request, errors=target.errors
        )

    @staticmethod
    def to_target(source: LLMFailedRequest) -> LLMFailedRequestDocument:
        response_type = source.request.params.response_type

        return LLMFailedRequestDocument(
            _id=source.id,
            _type=f'{response_type.__module__}.{response_type.__qualname__}',
            request=source.request,
            errors=source.errors,
        )
