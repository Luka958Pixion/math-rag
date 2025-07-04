from math_rag.application.models.inference import MMRequest
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MMRequestDocument

from .mm_params_mapping import MMParamsMapping
from .mm_router_params_mapping import MMRouterParamsMapping


class MMRequestMapping(BaseMapping[MMRequest, MMRequestDocument]):
    @staticmethod
    def to_source(target: MMRequestDocument) -> MMRequest:
        return MMRequest(
            id=target.id,
            text=target.text,
            params=MMParamsMapping.to_source(target.params),
            router_params=MMRouterParamsMapping.to_source(target.router_params)
            if target.router_params
            else None,
        )

    @staticmethod
    def to_target(source: MMRequest) -> MMRequestDocument:
        return MMRequestDocument(
            id=source.id,
            text=source.text,
            params=MMParamsMapping.to_target(source.params),
            router_params=MMRouterParamsMapping.to_target(source.router_params)
            if source.router_params
            else None,
        )
