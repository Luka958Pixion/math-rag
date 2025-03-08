from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class KCAssistantOutput(BaseModel):
    id: UUID = Field(default_factory=uuid4, exclude=True)
    katex: str
