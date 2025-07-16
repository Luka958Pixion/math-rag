from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MathProblemSolution(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    math_problem_id: UUID
    timestamp: datetime = Field(default_factory=datetime.now)
    text: str
