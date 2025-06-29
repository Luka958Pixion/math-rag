from abc import ABC
from uuid import UUID, uuid4

from pydantic import BaseModel, Field
from pydantic.json_schema import SkipJsonSchema

from .base_assistant_input import BaseAssistantInput


class BaseAssistantOutput(BaseModel, ABC):
    id: SkipJsonSchema[UUID] = Field(default_factory=uuid4)
    input_id: SkipJsonSchema[UUID]

    @classmethod
    def bind(cls, input_id: UUID) -> type['BaseAssistantOutput']:
        class BoundAssistantOutput(cls):
            def __init__(self, **kwargs):
                kwargs['input_id'] = input_id
                super().__init__(**kwargs)

        return BoundAssistantOutput

    @staticmethod
    def sort_by_input_id(
        inputs: list[BaseAssistantInput], outputs: list['BaseAssistantOutput']
    ) -> list['BaseAssistantOutput | None']:
        input_id_to_output = {output.input_id: output for output in outputs}

        return [input_id_to_output.get(input.id) for input in inputs]
