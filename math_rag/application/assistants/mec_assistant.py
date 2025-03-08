from math_rag.application.base.inference import BaseLLM
from math_rag.application.models.assistants import (
    MECAssistantInput,
    MECAssistantOutput,
)
from math_rag.application.models.inference import (
    LLMConversation,
    LLMMessage,
    LLMParams,
    LLMRequest,
    LLMResponseList,
)

from .models import MECAndLLMResponse
from .partials import PartialAssistant
from .prompts import MATH_EXPRESSION_CLASSIFICATION_PROMPT


class MathExpressionClassificationAssistant(
    PartialAssistant[MECAssistantInput, MECAssistantOutput, MECAndLLMResponse]
):
    def __init__(self, llm: BaseLLM):
        super().__init__(llm)

    def to_request(self, input: MECAssistantInput) -> LLMRequest[MECAndLLMResponse]:
        prompt = MATH_EXPRESSION_CLASSIFICATION_PROMPT.format(latex=input.latex)
        request = LLMRequest(
            conversation=LLMConversation(
                messages=[LLMMessage(role='user', content=prompt)]
            ),
            params=LLMParams[MECAndLLMResponse](
                model='gpt-4o-mini',
                temperature=0.0,
                response_type=MECAndLLMResponse,
            ),
        )

        return request

    def from_response_list(
        self, response_list: LLMResponseList[MECAndLLMResponse]
    ) -> MECAssistantOutput:
        label = response_list.responses[0].content.label
        output = MECAssistantOutput(label=label)

        return output
