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

    def create_request(
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

    def create_request_batch(
        self, latexes: list[str]
    ) -> LLMRequestBatch[MathExpressionClassificationResponse]:
        request_batch = LLMRequestBatch(
            requests=[self.create_request(latex) for latex in latexes]
        )

        return request_batch

    async def classify(self, latex: str) -> str:
        request = self.create_request(latex)
        responses = await self.llm.generate(request)
        label = responses[0].content.label

        return label

    async def batch_classify(
        self, latexes: list[str], delay: float, num_retries: int
    ) -> tuple[list[str], list[str]]:
        request_batch = self.create_request_batch(latexes)
        response_batch = await self.llm.batch_generate_retry(
            request_batch, MathExpressionClassificationResponse, delay, num_retries
        )
        labels = [
            response.content.label for response in response_batch.nested_responses[0]
        ]
        num_completed = len(response_batch.nested_responses)
        num_total = len(latexes)
        num_remaining = num_total - num_completed
        remaining_latexes = latexes[-num_remaining:]

        return remaining_latexes, labels

    async def batch_classify_init(self, latexes: list[str]) -> str:
        request_batch = self.create_request_batch(latexes)
        batch_id = await self.llm.batch_generate_init(request_batch)

        return batch_id

    async def batch_classify_result(self, batch_id: str) -> list[str] | None:
        response_batch = await self.llm.batch_generate_result(
            batch_id, MathExpressionClassificationResponse
        )

        if response_batch is None:
            return

        labels = [
            response.content.label for response in response_batch.nested_responses[0]
        ]

        return labels
