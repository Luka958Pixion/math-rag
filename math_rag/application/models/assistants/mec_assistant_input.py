from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class MECAssistantInput(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    latex: str
