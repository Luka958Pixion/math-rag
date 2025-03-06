from math_rag.application.base.inference import BaseLLM
from math_rag.application.models import (
    LLMConversation,
    LLMMessage,
    LLMParams,
    LLMRequest,
)

from .models import MathExpressionClassificationResponse
from .prompts import MATH_EXPRESSION_CLASSIFICATION_PROMPT


class MathExpressionClassificationAssistant:
    def __init__(self, llm: BaseLLM):
        self.llm = llm

    async def classify(self, latex: str) -> str:
        prompt = MATH_EXPRESSION_CLASSIFICATION_PROMPT.format(latex=latex)
        response_type = MathExpressionClassificationResponse
        request = LLMRequest(
            conversation=LLMConversation(
                messages=[LLMMessage(role='user', content=prompt)]
            ),
            params=LLMParams[response_type](
                model='gpt-4o-mini', temperature=0.0, response_type=response_type
            ),
        )
        responses = await self.llm.generate_json(request)
        label = responses[0].content.label

        return label
