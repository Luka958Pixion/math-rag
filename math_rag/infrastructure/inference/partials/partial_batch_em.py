from asyncio import sleep
from logging import getLogger

from math_rag.application.base.inference import BaseBatchEM
from math_rag.application.models.inference import (
    EMBatchRequest,
    EMBatchResult,
    EMResponseList,
)


logger = getLogger(__name__)


class PartialBatchEM(BaseBatchEM):
    async def _batch_embed(
        self,
        batch_request: EMBatchRequest,
        poll_interval: float,
    ) -> EMBatchResult:
        batch_id = await self.batch_embed_init(batch_request)

        while True:
            batch_result = await self.batch_embed_result(batch_id, batch_request.id)

            if batch_result is not None:
                return batch_result

            await sleep(poll_interval)

    async def _batch_embed_retry(
        self,
        batch_request: EMBatchRequest,
        *,
        poll_interval: float,
        max_num_retries: int,
    ) -> EMBatchResult:
        if max_num_retries < 0:
            raise ValueError()

        num_total = len(batch_request.requests)
        response_lists: list[EMResponseList] = []

        for _ in range(max_num_retries + 1):
            batch_result = await self._batch_embed(batch_request, poll_interval)
            response_lists.extend(batch_result.response_lists)

            if not batch_result.failed_requests:
                break

            batch_request = EMBatchRequest(
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

    async def batch_embed(
        self,
        batch_request: EMBatchRequest,
        *,
        poll_interval: float,
        max_num_retries: int,
    ) -> EMBatchResult:
        if max_num_retries:
            batch_result = await self._batch_embed_retry(
                batch_request,
                poll_interval=poll_interval,
                max_num_retries=max_num_retries,
            )

        batch_result = await self._batch_embed(batch_request, poll_interval)

        return batch_result
