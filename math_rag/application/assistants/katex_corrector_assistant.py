from math_rag.application.base.inference import (
    BaseBatchLLMRequestManagedScheduler,
    BaseManagedLLM,
)
from math_rag.application.enums.inference import LLMInferenceProvider, LLMModelProvider
from math_rag.application.models.assistants.inputs import KatexCorrector as Input
from math_rag.application.models.assistants.outputs import KatexCorrector as Output
from math_rag.application.models.inference import (
    LLMConversation,
    LLMMessage,
    LLMParams,
    LLMRequest,
    LLMResponseList,
    LLMRouterParams,
)

from .partials import PartialAssistant
from .prompts import KATEX_CORRECTOR_PROMPTS as PROMPTS


class KatexCorrectorAssistant(PartialAssistant[Input, Output]):
    def __init__(self, llm: BaseManagedLLM, scheduler: BaseBatchLLMRequestManagedScheduler | None):
        super().__init__(llm, scheduler)

    def encode_to_request(self, input: Input) -> LLMRequest[Output]:
        system_message_content = PROMPTS.system.format()
        user_message_content = PROMPTS.user.format(katex=input.katex, error=input.error)

        return LLMRequest(
            conversation=LLMConversation(
                messages=[
                    LLMMessage(role='system', content=system_message_content),
                    LLMMessage(role='user', content=user_message_content),
                ]
            ),
            params=LLMParams[Output](
                model='gpt-4.1-mini',
                temperature=0.0,
                response_type=Output.bind(input.id),
                metadata=dict(input_id=str(input.id)),
                store=True,
                max_completion_tokens=1024,
            ),
            router_params=LLMRouterParams(
                inference_provider=LLMInferenceProvider.OPEN_AI,
                model_provider=LLMModelProvider.OPEN_AI,
            ),
        )

    def decode_from_response_list(self, response_list: LLMResponseList[Output]) -> Output:
        return response_list.responses[0].content
