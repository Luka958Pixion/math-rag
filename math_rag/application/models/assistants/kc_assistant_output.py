from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema


class KCAssistantOutput(BaseModel):
    id: SkipJsonSchema[UUID] = Field(default_factory=uuid4)
    input_id: SkipJsonSchema[UUID]
    katex: str

    @classmethod
    def bind(cls, input_id: UUID):
        class _KCAssistantOutput(cls):
            def __init__(self, **data):
                super().__init__(**data, input_id=input_id)

        return _KCAssistantOutput
