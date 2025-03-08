from math_rag.application.base.inference import BaseLLM
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

from .partials import PartialAssistant
from .prompts import KATEX_CORRECTION_PROMPT


class KatexCorrectionAssistant(PartialAssistant[KCAssistantInput, KCAssistantOutput]):
    def __init__(self, llm: BaseLLM):
        super().__init__(llm)

    def to_request(self, input: KCAssistantInput) -> LLMRequest[KCAssistantOutput]:
        prompt = KATEX_CORRECTION_PROMPT.format(katex=input.katex, error=input.error)
        request = LLMRequest(
            conversation=LLMConversation(
                messages=[LLMMessage(role='user', content=prompt)]
            ),
            params=LLMParams[KCAssistantOutput](
                model='gpt-4o-mini',
                temperature=0.0,
                response_type=KCAssistantOutput,
            ),
        )

        return request

    def from_response_list(
        self, response_list: LLMResponseList[KCAssistantOutput]
    ) -> KCAssistantOutput:
        katex = response_list.responses[0].content.katex
        output = KCAssistantOutput(katex=katex)

        return output
