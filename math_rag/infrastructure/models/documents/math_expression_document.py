from datetime import datetime
from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class MathExpressionDocument(BaseDocument):
    id: UUID
    math_article_id: UUID
    dataset_id: UUID | None
    index_id: UUID | None
    timestamp: datetime
    latex: str
    katex: str | None
    position: int
    is_inline: bool
