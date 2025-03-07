from math_rag.application.base.inference import BaseLLM
from math_rag.application.base.services import BaseKatexValidatorService
from math_rag.application.models import (
    LLMConversation,
    LLMMessage,
    LLMParams,
    LLMRequest,
)

from .models import KatexCorrectionResponse
from .prompts import KATEX_CORRECTION_PROMPT


class KatexCorrectionAssistant:
    def __init__(
        self, llm: BaseLLM, katex_validation_service: BaseKatexValidatorService
    ):
        self.llm = llm
        self.katex_validation_service = katex_validation_service

    async def correct(self, katex: str, error: str) -> str | None:
        prompt = KATEX_CORRECTION_PROMPT.format(katex=katex, error=error)
        request = LLMRequest(
            conversation=LLMConversation(
                messages=[LLMMessage(role='user', content=prompt)]
            ),
            params=LLMParams[KatexCorrectionResponse](
                model='gpt-4o-mini',
                temperature=0.0,
                response_type=KatexCorrectionResponse,
            ),
        )
        responses = await self.llm.generate(request)
        katex = responses[0].content.katex
        result = await self.katex_validation_service.validate(katex)

        return katex if result.valid else None
