from pydantic import field_validator

from math_rag.application.base.assistants import BaseAssistantInput

from .kc_assistant_input import KCAssistantInput
from .kc_assistant_output import KCAssistantOutput


class KCRetryAssistantInput(BaseAssistantInput):
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
