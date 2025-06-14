from math_rag.application.base.inference import (
    BaseBatchLLMRequestManagedScheduler,
    BaseManagedLLM,
)
from math_rag.application.enums.inference import LLMInferenceProvider, LLMProvider
from math_rag.application.models.assistants import (
    KatexCorrectorRetryAssistantInput,
    KatexCorrectorRetryAssistantOutput,
)
from math_rag.application.models.inference import (
    LLMConversation,
    LLMMessage,
    LLMParams,
    LLMRequest,
    LLMResponseList,
)

from .partials import PartialAssistant
from .prompts import (
    KATEX_CORRECTOR_RETRY_USER_PROMPT,
    KATEX_CORRECTOR_SYSTEM_PROMPT,
    KATEX_CORRECTOR_USER_PROMPT,
)


class KatexCorrectorRetryAssistant(
    PartialAssistant[KatexCorrectorRetryAssistantInput, KatexCorrectorRetryAssistantOutput]
):
    def __init__(self, llm: BaseManagedLLM, scheduler: BaseBatchLLMRequestManagedScheduler | None):
        super().__init__(llm, scheduler)

    def encode_to_request(
        self, input: KatexCorrectorRetryAssistantInput
    ) -> LLMRequest[KatexCorrectorRetryAssistantOutput]:
        initial_input = input.pairs[0][0]
        initial_prompt = KATEX_CORRECTOR_USER_PROMPT.format(
            katex=initial_input.katex, error=initial_input.error
        )
        user_prompts = [
            KATEX_CORRECTOR_RETRY_USER_PROMPT.format(katex=input.katex, error=input.error)
            for input, _ in input.pairs[1:]
        ]
        user_prompts.insert(0, initial_prompt)

        outputs = [pair[1] for pair in input.pairs]

        system_prompt = KATEX_CORRECTOR_SYSTEM_PROMPT.format()
        system_message = LLMMessage(role='system', content=system_prompt)
        messages = [system_message]

        for user_prompt, output in zip(user_prompts, outputs):
            user_message = LLMMessage(role='user', content=user_prompt)
            messages.append(user_message)

            if output:
                assistant_message = LLMMessage(role='assistant', content=output.katex)
                messages.append(assistant_message)

        return LLMRequest(
            conversation=LLMConversation(messages=messages),
            params=LLMParams[KatexCorrectorRetryAssistantOutput](
                model='gpt-4.1',
                temperature=0.0,
                response_type=KatexCorrectorRetryAssistantOutput.bind(input.id),
                inference_provider=LLMInferenceProvider.OPEN_AI,
                model_provider=LLMProvider.OPEN_AI,
            ),
        )

    def decode_from_response_list(
        self, response_list: LLMResponseList[KatexCorrectorRetryAssistantOutput]
    ) -> KatexCorrectorRetryAssistantOutput:
        return response_list.responses[0].content
