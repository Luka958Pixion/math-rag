from uuid import UUID

from pydantic import BaseModel


class LLMMessageDocument(BaseModel):
    _id: UUID
    role: str
    content: str
