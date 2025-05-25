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
from .prompts import MATH_EXPRESSION_LABELER_PROMPT


class MathExpressionLabelerAssistant(
    PartialAssistant[
        MathExpressionLabelerAssistantInput, MathExpressionLabelerAssistantOutput
    ]
):
    def __init__(
        self, llm: BaseManagedLLM, scheduler: BaseBatchLLMRequestManagedScheduler | None
    ):
        super().__init__(llm, scheduler)

    def encode_to_request(
        self, input: MathExpressionLabelerAssistantInput
    ) -> LLMRequest[MathExpressionLabelerAssistantOutput]:
        prompt = MATH_EXPRESSION_LABELER_PROMPT.format(latex=input.latex)
        request = LLMRequest(
            conversation=LLMConversation(
                messages=[LLMMessage(role='user', content=prompt)]
            ),
            params=LLMParams[MathExpressionLabelerAssistantOutput](
                model='gpt-4.1-nano',
                temperature=0.0,
                response_type=MathExpressionLabelerAssistantOutput.bind(input.id),
            ),
        )

        return request

    def decode_from_response_list(
        self, response_list: LLMResponseList[MathExpressionLabelerAssistantOutput]
    ) -> MathExpressionLabelerAssistantOutput:
        return response_list.responses[0].content
