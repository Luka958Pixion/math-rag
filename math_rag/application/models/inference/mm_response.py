from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .mm_category import MMCategory


class MMResponse(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    categories: list[MMCategory]
