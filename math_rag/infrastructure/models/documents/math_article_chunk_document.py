from datetime import datetime
from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class MathArticleChunkDocument(BaseDocument):
    id: UUID
    math_article_id: UUID
    math_expression_index_id: UUID
    timestamp: datetime
    index: str
    indexes: list[int]
    text: str
