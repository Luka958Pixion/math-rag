from uuid import UUID

from pydantic import BaseModel


class LLMErrorDocument(BaseModel):
    _id: UUID
    message: str
    body: object | None
