from math_rag.application.base.inference import BaseManagedLLM
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

from .partials import PartialBatchAssistant
from .prompts import KATEX_CORRECTION_PROMPT, KATEX_CORRECTION_RETRY_PROMPT


class KCRetryAssistant(
    PartialBatchAssistant[KCRetryAssistantInput, KCRetryAssistantOutput]
):
    def __init__(self, llm: BaseManagedLLM):
        super().__init__(llm)

    def encode_to_request(
        self, input: KCRetryAssistantInput
    ) -> LLMRequest[KCRetryAssistantOutput]:
        initial_input = input.pairs[0][0]
        initial_prompt = KATEX_CORRECTION_PROMPT.format(
            katex=initial_input.katex, error=initial_input.error
        )
        prompts = [
            KATEX_CORRECTION_RETRY_PROMPT.format(katex=input.katex, error=input.error)
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
            params=LLMParams[KCRetryAssistantOutput](
                model='gpt-4o',
                temperature=0.0,
                response_type=KCRetryAssistantOutput.bind(input.id),
            ),
        )

        return request

    def decode_from_response_list(
        self, response_list: LLMResponseList[KCRetryAssistantOutput]
    ) -> KCRetryAssistantOutput:
        return response_list.responses[0].content
