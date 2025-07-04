from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MMParams(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    model: str
