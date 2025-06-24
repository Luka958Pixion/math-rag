from pydantic import field_validator

from math_rag.application.models.assistants.base import BaseAssistantInput

from ..outputs.katex_corrector import KatexCorrector as Output
from .katex_corrector import KatexCorrector as Input


class KatexCorrectorRetry(BaseAssistantInput):
    pairs: list[tuple[Input, Output | None]]

    @field_validator('pairs')
    def validate_pairs(
        cls,
        pairs: list[tuple[Input, Output | None]],
    ):
        if not pairs:
            return pairs

        if any(output is None for _, output in pairs[:-1]):
            raise ValueError('Only the last pair can have None output')

        return pairs
