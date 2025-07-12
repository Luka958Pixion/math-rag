from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MathExpressionContext(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    math_article_id: UUID
    math_expression_id: UUID
    math_expression_index_id: UUID
    timestamp: datetime = Field(default_factory=datetime.now)
    text: str
