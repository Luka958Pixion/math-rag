from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class MathExpressionClassificationDocument(BaseDocument):
    id: UUID
    math_expression_id: UUID
    value: str
