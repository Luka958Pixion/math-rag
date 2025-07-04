from abc import ABC
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class BaseEmbedderInput(BaseModel, ABC):
    id: UUID = Field(default_factory=uuid4)
