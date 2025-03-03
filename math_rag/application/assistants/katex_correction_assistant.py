from math_rag.application.base.inference import BaseLLM
from math_rag.application.base.services import BaseKatexValidationService
from math_rag.application.models import LLMParams


class KatexCorrectionAssistant:
    def __init__(
        self, llm: BaseLLM, katex_validation_service: BaseKatexValidationService
    ):
        self.llm = llm
        self.katex_validation_service = katex_validation_service

    async def correct(self, katex: str) -> str:
        result = self.katex_validation_service.validate(katex)

        if result.valid:
            return katex

        prompt = ...
        params = LLMParams(...)

        katex = await self.llm.generate(prompt, params)
        result = self.katex_validation_service.validate(katex)

        if not result.valid:
            raise Exception('KaTeX correction failed')

        return katex
