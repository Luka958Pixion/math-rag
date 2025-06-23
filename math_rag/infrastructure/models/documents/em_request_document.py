from uuid import UUID

from math_rag.infrastructure.base import BaseDocument

from .em_params_document import EMParamsDocument
from .em_router_params_document import EMRouterParamsDocument


class EMRequestDocument(BaseDocument):
    id: UUID
    text: str
    params: EMParamsDocument
    router_params: EMRouterParamsDocument | None
