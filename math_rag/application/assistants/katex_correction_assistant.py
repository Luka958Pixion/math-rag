from math_rag.application.base.inference import BaseLLM
from math_rag.application.base.services import BaseKatexValidatorService
from math_rag.application.models import LLMParams

from .models import KatexCorrectionResponse
from .prompts import KATEX_CORRECTION_PROMPT


class KatexCorrectionAssistant:
    def __init__(
        self, llm: BaseLLM, katex_validation_service: BaseKatexValidatorService
    ):
        self.llm = llm
        self.katex_validation_service = katex_validation_service

    async def correct(self, katex: str, error: str) -> str:
        result = await self.katex_validation_service.validate(katex)

        if result.valid:
            return katex

        params = LLMParams(
            model='gpt-4o-mini',
            temperature=0.0,
        )
        prompt = KATEX_CORRECTION_PROMPT.format(katex=katex, error=error)
        katex_correction_response = await self.llm.generate_json(
            prompt=prompt,
            params=params,
            response_model_type=KatexCorrectionResponse,
        )
        katex = katex_correction_response.katex
        result = await self.katex_validation_service.validate(katex)

        if not result.valid:
            raise Exception('KaTeX correction failed')

        return katex
