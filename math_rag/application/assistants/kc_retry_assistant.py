from math_rag.application.base.inference import BaseLLM
from math_rag.application.models.assistants import (
    KCRetryAssistantInput,
    KCRetryAssistantOutput,
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


class KatexCorrectionRetryAssistant(
    PartialAssistant[KCRetryAssistantInput, KCRetryAssistantOutput]
):
    def __init__(self, llm: BaseLLM):
        super().__init__(llm)

    def to_request(
        self, input: KCRetryAssistantInput
    ) -> LLMRequest[KCRetryAssistantOutput]:
        prompt = KATEX_CORRECTION_PROMPT.format(katex=input.katex, error=input.error)
        request = LLMRequest(
            conversation=LLMConversation(
                messages=[LLMMessage(role='user', content=prompt)]
            ),
            params=LLMParams[KCRetryAssistantOutput](
                model='gpt-4o-mini',
                temperature=0.0,
                response_type=KCRetryAssistantOutput,
            ),
        )

        return request

    def from_response_list(
        self, response_list: LLMResponseList[KCRetryAssistantOutput]
    ) -> KCRetryAssistantOutput:
        output = response_list.responses[0].content

        return output
