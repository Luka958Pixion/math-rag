from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MathExpressionRelationshipDescription(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    math_expression_index_id: UUID
    math_expression_relationship_id: UUID
    timestamp: datetime = Field(default_factory=datetime.now)
    description: str
