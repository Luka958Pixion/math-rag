from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MathExpression(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    math_article_id: UUID
    math_expression_dataset_id: UUID | None
    math_expression_group_id: UUID | None
    math_expression_index_id: UUID | None
    timestamp: datetime = Field(default_factory=datetime.now)
    latex: str
    katex: str | None
    index: int
    position: int
    is_inline: bool
