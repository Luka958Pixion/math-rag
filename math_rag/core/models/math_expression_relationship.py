from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MathExpressionRelationship(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    math_article_chunk_id: UUID
    math_expression_index_id: UUID
    math_expression_source_id: UUID
    math_expression_target_id: UUID
    math_expression_source_index: int
    math_expression_target_index: int
    timestamp: datetime = Field(default_factory=datetime.now)
