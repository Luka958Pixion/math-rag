from math_rag.application.base.inference import BaseManagedLLM
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
from .prompts import KATEX_CORRECTOR_PROMPT, KATEX_CORRECTOR_RETRY_PROMPT


class KatexCorrectorRetryAssistant(
    PartialAssistant[
        KatexCorrectorRetryAssistantInput, KatexCorrectorRetryAssistantOutput
    ]
):
    def __init__(self, llm: BaseManagedLLM):
        super().__init__(llm)

    def encode_to_request(
        self, input: KatexCorrectorRetryAssistantInput
    ) -> LLMRequest[KatexCorrectorRetryAssistantOutput]:
        initial_input = input.pairs[0][0]
        initial_prompt = KATEX_CORRECTOR_PROMPT.format(
            katex=initial_input.katex, error=initial_input.error
        )
        prompts = [
            KATEX_CORRECTOR_RETRY_PROMPT.format(katex=input.katex, error=input.error)
            for input, _ in input.pairs[1:]
        ]
        prompts.insert(0, initial_prompt)

        outputs = [pair[1] for pair in input.pairs]
        messages = []

        for prompt, output in zip(prompts, outputs):
            user_message = LLMMessage(role='user', content=prompt)
            messages.append(user_message)

            if output:
                assistant_message = LLMMessage(role='assistant', content=output.katex)
                messages.append(assistant_message)

        request = LLMRequest(
            conversation=LLMConversation(messages=messages),
            params=LLMParams[KatexCorrectorRetryAssistantOutput](
                model='gpt-4o',
                temperature=0.0,
                response_type=KatexCorrectorRetryAssistantOutput.bind(input.id),
            ),
        )

        return request

    def decode_from_response_list(
        self, response_list: LLMResponseList[KatexCorrectorRetryAssistantOutput]
    ) -> KatexCorrectorRetryAssistantOutput:
        return response_list.responses[0].content
