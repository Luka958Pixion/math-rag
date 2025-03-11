from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class LLMMessage(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    role: str
    content: str
