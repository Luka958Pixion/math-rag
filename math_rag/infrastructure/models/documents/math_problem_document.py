from datetime import datetime
from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class MathProblemDocument(BaseDocument):
    id: UUID
    math_expression_index_id: UUID
    timestamp: datetime
    file_path: str | None
    url: str | None
