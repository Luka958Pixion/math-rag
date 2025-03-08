from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class KCAssistantInput(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    katex: str
    error: str
