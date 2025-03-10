from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from .kc_assistant_input import KCAssistantInput
from .kc_assistant_output import KCAssistantOutput


class KCRetryAssistantInput(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    pairs: list[tuple[KCAssistantInput, KCAssistantOutput | None]]

    @field_validator('pairs')
    @classmethod
    def validate_pairs(
        cls, pairs: list[tuple[KCAssistantInput, KCAssistantOutput | None]]
    ):
        if not pairs:
            return pairs

        if any(output is None for _, output in pairs[:-1]):
            raise ValueError('Only the last pair can have None output')

        return pairs
