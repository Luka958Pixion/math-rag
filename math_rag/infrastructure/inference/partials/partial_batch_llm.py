from asyncio import sleep
from logging import getLogger

from math_rag.application.base.inference import BaseBatchLLM
from math_rag.application.models.inference import (
    LLMBatchRequest,
    LLMBatchResult,
    LLMResponseList,
)
from math_rag.application.types.inference import LLMResponseType


logger = getLogger(__name__)


class PartialBatchLLM(BaseBatchLLM):
    async def _batch_generate(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
        response_type: type[LLMResponseType],
        *,
        poll_interval: float,
        max_tokens_per_day: float | None,
    ) -> LLMBatchResult[LLMResponseType]:
        batch_id = await self.batch_generate_init(
            batch_request, max_tokens_per_day=max_tokens_per_day
        )

        while True:
            batch_result = await self.batch_generate_result(
                batch_id, batch_request.id, response_type
            )

            if batch_result is not None:
                return batch_result

            await sleep(poll_interval)

    async def _batch_generate_retry(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
        response_type: type[LLMResponseType],
        *,
        poll_interval: float,
        max_tokens_per_day: float | None,
        max_num_retries: int,
    ) -> LLMBatchResult[LLMResponseType]:
        if max_num_retries < 0:
            raise ValueError()

        num_total = len(batch_request.requests)
        response_lists: list[LLMResponseList[LLMResponseType]] = []

        for _ in range(max_num_retries + 1):
            batch_result = await self._batch_generate(
                batch_request,
                response_type,
                poll_interval=poll_interval,
                max_tokens_per_day=max_tokens_per_day,
            )
            response_lists.extend(batch_result.response_lists)

            if not batch_result.failed_requests:
                break

            batch_request = LLMBatchRequest(
                requests=[
                    failed_request.request
                    for failed_request in batch_result.failed_requests
                ]
            )

        batch_result.response_lists = response_lists
        num_completed = len(response_lists)

        logger.info(
            f'Completed {num_completed}/{num_total} requests within {max_num_retries} retries'
        )

        return batch_result

    async def batch_generate(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
        response_type: type[LLMResponseType],
        *,
        poll_interval: float,
        max_tokens_per_day: float | None,
        max_num_retries: int,
    ) -> LLMBatchResult[LLMResponseType]:
        if max_num_retries:
            batch_result = await self._batch_generate_retry(
                batch_request,
                response_type,
                poll_interval=poll_interval,
                max_tokens_per_day=max_tokens_per_day,
                max_num_retries=max_num_retries,
            )

        batch_result = await self._batch_generate(
            batch_request,
            response_type,
            poll_interval=poll_interval,
            max_tokens_per_day=max_tokens_per_day,
        )

        return batch_result
