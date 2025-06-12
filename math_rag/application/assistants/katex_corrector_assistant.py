from math_rag.application.base.inference import (
    BaseBatchLLMRequestManagedScheduler,
    BaseManagedLLM,
)
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
from .prompts import KATEX_CORRECTOR_SYSTEM_PROMPT, KATEX_CORRECTOR_USER_PROMPT


class KatexCorrectorAssistant(
    PartialAssistant[KatexCorrectorAssistantInput, KatexCorrectorAssistantOutput]
):
    def __init__(self, llm: BaseManagedLLM, scheduler: BaseBatchLLMRequestManagedScheduler | None):
        super().__init__(llm, scheduler)

    def encode_to_request(
        self, input: KatexCorrectorAssistantInput
    ) -> LLMRequest[KatexCorrectorAssistantOutput]:
        system_prompt = KATEX_CORRECTOR_SYSTEM_PROMPT.format()
        user_prompt = KATEX_CORRECTOR_USER_PROMPT.format(katex=input.katex, error=input.error)

        return LLMRequest(
            conversation=LLMConversation(
                messages=[
                    LLMMessage(role='system', content=system_prompt),
                    LLMMessage(role='user', content=user_prompt),
                ]
            ),
            params=LLMParams[KatexCorrectorAssistantOutput](
                model='gpt-4.1-nano',
                temperature=0.0,
                response_type=KatexCorrectorAssistantOutput.bind(input.id),
                metadata={'input_id': str(input.id)},
                store=True,
                max_completion_tokens=1024,
            ),
        )

    def decode_from_response_list(
        self, response_list: LLMResponseList[KatexCorrectorAssistantOutput]
    ) -> KatexCorrectorAssistantOutput:
        return response_list.responses[0].content
