from uuid import UUID

from math_rag.infrastructure.base import BaseDocument

from .em_error_document import EMErrorDocument
from .em_request_document import EMRequestDocument


class EMFailedRequestDocument(BaseDocument):
    id: UUID
    request: EMRequestDocument
    errors: list[EMErrorDocument]
