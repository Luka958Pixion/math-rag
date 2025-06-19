from datetime import datetime
from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class MathExpressionDatasetDocument(BaseDocument):
    # NOTE: samples don't go here because they would exceed the document size limit
    id: UUID
    timestamp: datetime
    build_stage: str
    build_from_id: UUID | None
    build_from_stage: str | None
    build_priority: str

    # NOTE: build_details are flattened
    categories: list[tuple[str, str]]
    category_limit: int
    splits: list[tuple[str, float]]
