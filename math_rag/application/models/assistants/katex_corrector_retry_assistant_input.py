from pydantic import field_validator

from math_rag.application.base.assistants import BaseAssistantInput

from .katex_corrector_assistant_input import KatexCorrectorAssistantInput
from .katex_corrector_assistant_output import KatexCorrectorAssistantOutput


class KatexCorrectorRetryAssistantInput(BaseAssistantInput):
    pairs: list[
        tuple[KatexCorrectorAssistantInput, KatexCorrectorAssistantOutput | None]
    ]

    @field_validator('pairs')
    def validate_pairs(
        cls,
        pairs: list[
            tuple[KatexCorrectorAssistantInput, KatexCorrectorAssistantOutput | None]
        ],
    ):
        if not pairs:
            return pairs

        if any(output is None for _, output in pairs[:-1]):
            raise ValueError('Only the last pair can have None output')

        return pairs
