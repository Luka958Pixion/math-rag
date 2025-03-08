from math_rag.application.base.inference import BaseLLM
from math_rag.application.base.services import BaseKatexValidatorService
from math_rag.application.models.assistants import (
    KCAssistantInput,
    KCAssistantOutput,
)
from math_rag.application.models.inference import (
    LLMConversation,
    LLMMessage,
    LLMParams,
    LLMRequest,
    LLMResponseList,
)

from .models import KCAndLLMResponse
from .partials import PartialAssistant
from .prompts import KATEX_CORRECTION_PROMPT


class KatexCorrectionAssistant(
    PartialAssistant[KCAssistantInput, KCAssistantOutput, KCAndLLMResponse]
):
    def __init__(
        self, llm: BaseLLM, katex_validation_service: BaseKatexValidatorService
    ):
        self.llm = llm
        self.katex_validation_service = katex_validation_service

    def to_request(self, input: KCAssistantInput) -> LLMRequest[KCAndLLMResponse]:
        prompt = KATEX_CORRECTION_PROMPT.format(katex=input.katex, error=input.error)
        request = LLMRequest(
            conversation=LLMConversation(
                messages=[LLMMessage(role='user', content=prompt)]
            ),
            params=LLMParams[KCAndLLMResponse](
                model='gpt-4o-mini',
                temperature=0.0,
                response_type=KCAndLLMResponse,
            ),
        )

        return request

    def from_response_list(
        self, response_list: LLMResponseList[KCAndLLMResponse]
    ) -> KCAssistantOutput:
        katex = response_list.responses[0].content.label
        output = KCAssistantOutput(label=katex)

        return output
