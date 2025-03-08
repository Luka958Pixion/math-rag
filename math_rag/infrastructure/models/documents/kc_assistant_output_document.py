from uuid import UUID

from pydantic import BaseModel


class KCAssistantOutputDocument(BaseModel):
    _id: UUID
    katex: str
