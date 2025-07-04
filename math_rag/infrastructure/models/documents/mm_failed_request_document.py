from uuid import UUID

from math_rag.infrastructure.base import BaseDocument

from .mm_error_document import MMErrorDocument
from .mm_request_document import MMRequestDocument


class MMFailedRequestDocument(BaseDocument):
    id: UUID
    request: MMRequestDocument
    errors: list[MMErrorDocument]
