from math_rag.application.base.inference import BaseManagedLLM
from math_rag.application.models.assistants import (
    KatexCorrectorAssistantInput,
    KatexCorrectorAssistantOutput,
)
from math_rag.application.models.inference import (
    LLMConversation,
    LLMMessage,
    LLMParams,
    LLMRequest,
    LLMResponseList,
)

from .partials import PartialAssistant
from .prompts import KATEX_CORRECTOR_PROMPT


class KatexCorrectorAssistant(
    PartialAssistant[KatexCorrectorAssistantInput, KatexCorrectorAssistantOutput]
):
    def __init__(self, llm: BaseManagedLLM):
        super().__init__(llm)

    def encode_to_request(
        self, input: KatexCorrectorAssistantInput
    ) -> LLMRequest[KatexCorrectorAssistantOutput]:
        prompt = KATEX_CORRECTOR_PROMPT.format(katex=input.katex, error=input.error)
        request = LLMRequest(
            conversation=LLMConversation(
                messages=[LLMMessage(role='user', content=prompt)]
            ),
            params=LLMParams[KatexCorrectorAssistantOutput](
                model='gpt-4o-mini',
                temperature=0.0,
                response_type=KatexCorrectorAssistantOutput.bind(input.id),
                metadata={'input_id': str(input.id)},
                store=True,
            ),
        )

        return request

    def decode_from_response_list(
        self, response_list: LLMResponseList[KatexCorrectorAssistantOutput]
    ) -> KatexCorrectorAssistantOutput:
        return response_list.responses[0].content
