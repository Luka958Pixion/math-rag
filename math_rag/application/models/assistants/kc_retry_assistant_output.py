from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema


class KCRetryAssistantOutput(BaseModel):
    id: SkipJsonSchema[UUID] = Field(default_factory=uuid4)
    katex: str
