from math_rag.application.models.inference import EMRequest
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import EMRequestDocument

from .em_params_mapping import EMParamsMapping
from .em_router_params_mapping import EMRouterParamsMapping


class EMRequestMapping(BaseMapping[EMRequest, EMRequestDocument]):
    @staticmethod
    def to_source(target: EMRequestDocument) -> EMRequest:
        return EMRequest(
            id=target.id,
            text=target.text,
            params=EMParamsMapping.to_source(target.params),
            router_params=EMRouterParamsMapping.to_source(target.router_params),
        )

    @staticmethod
    def to_target(source: EMRequest) -> EMRequestDocument:
        return EMRequestDocument(
            id=source.id,
            text=source.text,
            params=EMParamsMapping.to_target(source.params),
            router_params=EMRouterParamsMapping.to_target(source.router_params),
        )
