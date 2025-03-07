from math_rag.application.base.inference import BaseLLM
from math_rag.application.models import (
    LLMConversation,
    LLMMessage,
    LLMParams,
    LLMRequest,
    LLMRequestBatch,
)

from .models import MathExpressionClassificationResponse
from .prompts import MATH_EXPRESSION_CLASSIFICATION_PROMPT


class MathExpressionClassificationAssistant:
    def __init__(self, llm: BaseLLM):
        self.llm = llm

    async def classify(self, latex: str) -> str:
        prompt = MATH_EXPRESSION_CLASSIFICATION_PROMPT.format(latex=latex)
        request = LLMRequest(
            conversation=LLMConversation(
                messages=[LLMMessage(role='user', content=prompt)]
            ),
            params=LLMParams[MathExpressionClassificationResponse](
                model='gpt-4o-mini',
                temperature=0.0,
                response_type=MathExpressionClassificationResponse,
            ),
        )
        responses = await self.llm.generate(request)
        label = responses[0].content.label

        return label

    async def batch_classify(self, latexes: list[str]) -> list[str]:
        prompts = [
            MATH_EXPRESSION_CLASSIFICATION_PROMPT.format(latex=latex)
            for latex in latexes
        ]
        request_batch = LLMRequestBatch(
            requests=[
                LLMRequest(
                    conversation=LLMConversation(
                        messages=[LLMMessage(role='user', content=prompt)]
                    ),
                    params=LLMParams[MathExpressionClassificationResponse](
                        model='gpt-4o-mini',
                        temperature=0.0,
                        response_type=MathExpressionClassificationResponse,
                    ),
                )
                for prompt in prompts
            ]
        )
        response_batch = await self.llm.batch_generate(
            request_batch, MathExpressionClassificationResponse
        )
        # TODO response_batch.incomplete_request_batch

        if response_batch is None:
            raise ValueError()

        labels = [
            response.content.label for response in response_batch.nested_responses[0]
        ]

        return labels
