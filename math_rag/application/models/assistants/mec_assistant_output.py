from functools import partial
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema


class MECAssistantOutput(BaseModel):
    id: SkipJsonSchema[UUID] = Field(default_factory=uuid4)
    input_id: SkipJsonSchema[UUID]
    label: str = Field(alias='class')

    @classmethod
    def bind(cls, input_id: UUID) -> type['MECAssistantOutput']:
        return partial(cls, input_id=input_id)
