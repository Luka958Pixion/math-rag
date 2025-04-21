from math_rag.application.models.inference import EMFailedRequest
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import EMFailedRequestDocument

from .em_request_mapping import EMRequestMapping


class EMFailedRequestMapping(BaseMapping[EMFailedRequest, EMFailedRequestDocument]):
    @staticmethod
    def to_source(target: EMFailedRequestDocument) -> EMFailedRequest:
        return EMFailedRequest(
            id=target.id,
            request=EMRequestMapping.to_source(target.request),
            errors=target.errors,
        )

    @staticmethod
    def to_target(source: EMFailedRequest) -> EMFailedRequestDocument:
        return EMFailedRequestDocument(
            id=source.id,
            request=EMRequestMapping.to_target(source.request),
            errors=source.errors,
        )
