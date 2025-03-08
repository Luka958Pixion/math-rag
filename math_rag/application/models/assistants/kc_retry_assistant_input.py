from pydantic import BaseModel, field_validator

from .kc_assistant_input import KCAssistantInput
from .kc_assistant_output import KCAssistantOutput


class KCRetryAssistantInput(BaseModel):
    pairs: list[tuple[KCAssistantInput, KCAssistantOutput | None]]

    @field_validator('pairs')
    def validate_pairs(pairs):
        if not pairs:
            return pairs

        if any(output is None for _, output in pairs[:-1]):
            raise ValueError('Only the last pair can have None output')

        return pairs
