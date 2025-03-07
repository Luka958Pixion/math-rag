import logging

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

    def _get_request_batch(
        self, latexes: list[str]
    ) -> LLMRequestBatch[MathExpressionClassificationResponse]:
        request_batch = LLMRequestBatch(
            requests=[self._get_request(latex) for latex in latexes]
        )

        return request_batch

    async def classify(self, latex: str) -> str:
        request = self._get_request(latex)
        responses = await self.llm.generate(request)
        label = responses[0].content.label

        return label

    async def batch_classify(self, latexes: list[str], retries: int) -> list[str]:
        if retries < 0:
            raise ValueError()

        request_batch = self._get_request_batch(latexes)
        labels: list[str] = []

        for _ in range(retries + 1):
            response_batch = await self.llm.batch_generate(
                request_batch, MathExpressionClassificationResponse
            )

            if response_batch is None:
                raise ValueError()

            labels_batch = [
                response.content.label
                for response in response_batch.nested_responses[0]
            ]
            labels.extend(labels_batch)

            if not response_batch.incomplete_request_batch.requests:
                break

            request_batch = response_batch.incomplete_request_batch

        if response_batch.incomplete_request_batch.requests:
            logging.info(
                f'{self.batch_classify.__name__} completed {len(labels)}/{len(latexes)} requests within {retries} retries'
            )

        return labels

    async def batch_classify_init(self, latexes: list[str]) -> str:
        request_batch = self._get_request_batch(latexes)
        batch_id = await self.llm.batch_generate_init(request_batch)

        return batch_id

    async def batch_classify_result(self, batch_id: str) -> list[str]:
        response_batch = await self.llm.batch_generate_result(
            batch_id, MathExpressionClassificationResponse
        )

        if response_batch is None:
            raise ValueError()

        labels = [
            response.content.label for response in response_batch.nested_responses[0]
        ]

        if response_batch.incomplete_request_batch.requests:
            total = len(labels) + len(response_batch.incomplete_request_batch.requests)
            logging.info(
                f'{self.batch_classify.__name__} completed {len(labels)}/{total} requests'
            )

        return labels
