from math_rag.application.base.inference import (
    BaseBatchLLMRequestManagedScheduler,
    BaseManagedLLM,
)
from math_rag.application.enums.inference import LLMInferenceProvider, LLMModelProvider
from math_rag.application.models.assistants import (
    KatexCorrectorRetryAssistantInput as Input,
)
from math_rag.application.models.assistants import (
    KatexCorrectorRetryAssistantOutput as Output,
)
from math_rag.application.models.inference import (
    LLMConversation,
    LLMMessage,
    LLMParams,
    LLMRequest,
    LLMResponseList,
    LLMRouterParams,
)

from .partials import PartialAssistant
from .prompts import KATEX_CORRECTOR_PROMPTS as PROMTPS
from .prompts import KATEX_CORRECTOR_RETRY_USER_PROMPT


class KatexCorrectorRetryAssistant(PartialAssistant[Input, Output]):
    def __init__(self, llm: BaseManagedLLM, scheduler: BaseBatchLLMRequestManagedScheduler | None):
        super().__init__(llm, scheduler)

        self.model = 'gpt-4.1-nano'
        self.temperature = 0.0
        self.store = True
        self.max_completion_tokens = 1024
        self.inference_provider = LLMInferenceProvider.OPEN_AI
        self.model_provider = LLMModelProvider.OPEN_AI

    def encode_to_request(self, input: Input) -> LLMRequest[Output]:
        initial_input = input.pairs[0][0]
        initial_prompt = PROMTPS.user.format(katex=initial_input.katex, error=initial_input.error)
        user_message_contents = [
            KATEX_CORRECTOR_RETRY_USER_PROMPT.format(katex=input.katex, error=input.error)
            for input, _ in input.pairs[1:]
        ]
        user_message_contents.insert(0, initial_prompt)

        outputs = [pair[1] for pair in input.pairs]

        system_message_content = PROMTPS.system.format()
        system_message = LLMMessage(role='system', content=system_message_content)
        messages = [system_message]

        for user_message_content, output in zip(user_message_contents, outputs):
            user_message = LLMMessage(role='user', content=user_message_content)
            messages.append(user_message)

            if output:
                assistant_message = LLMMessage(role='assistant', content=output.katex)
                messages.append(assistant_message)

        return LLMRequest(
            conversation=LLMConversation(messages=messages),
            params=LLMParams[Output](
                model=self.model,
                temperature=self.temperature,
                response_type=Output.bind(input.id),
                metadata=dict(input_id=str(input.id)),
                store=self.store,
                max_completion_tokens=self.max_completion_tokens,
            ),
            router_params=LLMRouterParams(
                inference_provider=self.inference_provider,
                model_provider=self.model_provider,
            ),
        )

    def decode_from_response_list(self, response_list: LLMResponseList[Output]) -> Output:
        return response_list.responses[0].content
