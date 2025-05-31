from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MathArticle(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    math_expression_dataset_id: UUID | None
    index_id: UUID | None
    timestamp: datetime = Field(default_factory=datetime.now)
    name: str
    bytes: bytes
