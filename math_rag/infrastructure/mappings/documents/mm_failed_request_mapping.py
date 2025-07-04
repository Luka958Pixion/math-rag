from math_rag.application.models.inference import MMFailedRequest
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MMFailedRequestDocument

from .mm_request_mapping import MMRequestMapping


class MMFailedRequestMapping(BaseMapping[MMFailedRequest, MMFailedRequestDocument]):
    @staticmethod
    def to_source(target: MMFailedRequestDocument) -> MMFailedRequest:
        return MMFailedRequest(
            id=target.id,
            request=MMRequestMapping.to_source(target.request),
            errors=target.errors,
        )

    @staticmethod
    def to_target(source: MMFailedRequest) -> MMFailedRequestDocument:
        return MMFailedRequestDocument(
            id=source.id,
            request=MMRequestMapping.to_target(source.request),
            errors=source.errors,
        )
