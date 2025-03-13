from abc import ABC
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema


class BaseAssistantInput(BaseModel, ABC):
    id: SkipJsonSchema[UUID] = Field(default_factory=uuid4)
