from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MathProblemSolution(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.now)
