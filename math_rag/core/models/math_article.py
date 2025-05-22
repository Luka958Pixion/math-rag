from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MathArticle(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    index_id: UUID
    timestamp: datetime = Field(default_factory=datetime.now)
    name: str
    bytes: bytes
