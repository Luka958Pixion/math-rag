from math_rag.application.base.inference import (
    BaseBatchLLMRequestManagedScheduler,
    BaseManagedLLM,
)
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
)

from .partials import PartialAssistant
from .prompts import MATH_EXPRESSION_LABELER_SYSTEM_PROMPT, MATH_EXPRESSION_LABELER_USER_PROMPT


class MathExpressionLabelerAssistant(
    PartialAssistant[MathExpressionLabelerAssistantInput, MathExpressionLabelerAssistantOutput]
):
    def __init__(self, llm: BaseManagedLLM, scheduler: BaseBatchLLMRequestManagedScheduler | None):
        super().__init__(llm, scheduler)

    def encode_to_request(
        self, input: MathExpressionLabelerAssistantInput
    ) -> LLMRequest[MathExpressionLabelerAssistantOutput]:
        system_prompt = MATH_EXPRESSION_LABELER_SYSTEM_PROMPT.format()
        user_prompt = MATH_EXPRESSION_LABELER_USER_PROMPT.format(latex=input.latex)

        return LLMRequest(
            conversation=LLMConversation(
                messages=[
                    LLMMessage(role='system', content=system_prompt),
                    LLMMessage(role='user', content=user_prompt),
                ]
            ),
            params=LLMParams[MathExpressionLabelerAssistantOutput](
                model='gpt-4.1-nano',
                temperature=0.0,
                response_type=MathExpressionLabelerAssistantOutput.bind(input.id),
            ),
        )

    def decode_from_response_list(
        self, response_list: LLMResponseList[MathExpressionLabelerAssistantOutput]
    ) -> MathExpressionLabelerAssistantOutput:
        return response_list.responses[0].content
