from typing import Type

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

    def _get_request(
        self, latex: str
    ) -> LLMRequest[MathExpressionClassificationResponse]:
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

        return request

    async def classify(self, latex: str) -> str:
        request = self._get_request(latex)
        responses = await self.llm.generate(request)
        label = responses[0].content.label

        return label

    async def batch_classify(self, latexes: list[str]) -> list[str]:
        request_batch = LLMRequestBatch(
            requests=[self._get_request(latex) for latex in latexes]
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

    async def batch_classify_init(self, latexes: list[str]) -> str:
        request_batch = LLMRequestBatch(
            requests=[self._get_request(latex) for latex in latexes]
        )
        batch_id = await self.llm.batch_generate_init(request_batch)

        return batch_id

    async def batch_classify_result(self, batch_id: str) -> list[str]:
        response_batch = await self.llm.batch_generate_result(
            batch_id, MathExpressionClassificationResponse
        )

        # TODO response_batch.incomplete_request_batch

        if response_batch is None:
            raise ValueError()

        labels = [
            response.content.label for response in response_batch.nested_responses[0]
        ]

        return labels
