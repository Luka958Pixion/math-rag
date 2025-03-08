from uuid import UUID

from pydantic import BaseModel


class MathExpressionClassificationDocument(BaseModel):
    _id: UUID
    math_expression_id: UUID
    value: str
