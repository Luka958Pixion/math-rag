from uuid import UUID

from math_rag.infrastructure.base import BaseDocument

from .mm_params_document import MMParamsDocument
from .mm_router_params_document import MMRouterParamsDocument


class MMRequestDocument(BaseDocument):
    id: UUID
    text: str
    params: MMParamsDocument
    router_params: MMRouterParamsDocument | None
