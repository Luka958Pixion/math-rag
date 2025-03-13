from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema


class KCAssistantOutput(BaseModel):
    id: SkipJsonSchema[UUID] = Field(default_factory=uuid4)
    input_id: SkipJsonSchema[UUID]
    katex: str

    @classmethod
    def bind(cls, input_id: UUID) -> type['KCAssistantOutput']:
        class BoundKCAssistantOutput(cls):
            def __init__(self, **kwargs):
                kwargs['input_id'] = input_id
                super().__init__(**kwargs)

        return BoundKCAssistantOutput
