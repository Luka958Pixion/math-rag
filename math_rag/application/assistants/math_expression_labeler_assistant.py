from math_rag.application.base.inference import (
    BaseBatchLLMRequestManagedScheduler,
    BaseManagedLLM,
)
from math_rag.application.enums.inference import LLMInferenceProvider, LLMModelProvider
from math_rag.application.models.assistants import (
    MathExpressionLabelerAssistantInput,
    MathExpressionLabelerAssistantOutput,
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
from .prompts import _SYSTEM_PROMPT, _USER_PROMPT


class MathExpressionLabelerAssistant(
    PartialAssistant[MathExpressionLabelerAssistantInput, MathExpressionLabelerAssistantOutput]
):
    def __init__(self, llm: BaseManagedLLM, scheduler: BaseBatchLLMRequestManagedScheduler | None):
        super().__init__(llm, scheduler)

        self.system_prompt = _SYSTEM_PROMPT
        self.user_prompt = _USER_PROMPT
        self.model = 'gpt-4.1-nano'
        self.temperature = 0.0
        self.store = True
        self.max_completion_tokens = 50
        self.inference_provider = LLMInferenceProvider.OPEN_AI
        self.model_provider = LLMModelProvider.OPEN_AI

    def encode_to_request(
        self, input: MathExpressionLabelerAssistantInput
    ) -> LLMRequest[MathExpressionLabelerAssistantOutput]:
        system_message_content = self.system_prompt.format()
        user_message_content = self.user_prompt.format(latex=input.latex)

        return LLMRequest(
            conversation=LLMConversation(
                messages=[
                    LLMMessage(role='system', content=system_message_content),
                    LLMMessage(role='user', content=user_message_content),
                ]
            ),
            params=LLMParams[MathExpressionLabelerAssistantOutput](
                model=self.model,
                temperature=self.temperature,
                response_type=MathExpressionLabelerAssistantOutput.bind(input.id),
                metadata=dict(input_id=str(input.id)),
                store=self.store,
                max_completion_tokens=self.max_completion_tokens,
            ),
            router_params=LLMRouterParams(
                inference_provider=self.inference_provider,
                model_provider=self.model_provider,
            ),
        )

    def decode_from_response_list(
        self, response_list: LLMResponseList[MathExpressionLabelerAssistantOutput]
    ) -> MathExpressionLabelerAssistantOutput:
        return response_list.responses[0].content
