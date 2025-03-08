from uuid import UUID

from pydantic import BaseModel


class KCAssistantInputDocument(BaseModel):
    _id: UUID
    katex: str
    error: str
