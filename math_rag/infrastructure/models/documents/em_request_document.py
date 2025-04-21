from uuid import UUID

from math_rag.infrastructure.base import BaseDocument

from .em_params_document import EMParamsDocument


class EMRequestDocument(BaseDocument):
    id: UUID
    text: str
    params: EMParamsDocument
