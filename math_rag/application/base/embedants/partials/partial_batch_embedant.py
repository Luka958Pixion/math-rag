from uuid import UUID

from math_rag.application.base.assistants import BaseAssistantProtocol, BaseBatchAssistant
from math_rag.application.base.inference import (
    BaseBatchEMRequestManagedScheduler,
    BaseBatchManagedEM,
)
from math_rag.application.models.inference import EMBatchRequest, EMBatchResult
from math_rag.application.types.embedants import EmbedantInputType, EmbedantOutputType


class PartialBatchEmbedant(
    BaseBatchAssistant[EmbedantInputType, EmbedantOutputType],
    BaseAssistantProtocol[EmbedantInputType, EmbedantOutputType],
):
    def __init__(
        self,
        em: BaseBatchManagedEM,
        scheduler: BaseBatchEMRequestManagedScheduler | None,
    ):
        self._em = em
        self._scheduler = scheduler

    def _inputs_to_batch_request(
        self, inputs: list[EmbedantInputType]
    ) -> EMBatchRequest[EmbedantOutputType]:
        return EMBatchRequest(requests=[self.encode_to_request(input) for input in inputs])

    def _batch_result_to_outputs(
        self, batch_result: EMBatchResult[EmbedantOutputType]
    ) -> list[EmbedantOutputType]:
        return [
            self.decode_from_response_list(response_list)
            for response_list in batch_result.response_lists
        ]

    async def batch_assist(
        self, inputs: list[EmbedantInputType], *, use_scheduler: bool
    ) -> list[EmbedantOutputType]:
        batch_request = self._inputs_to_batch_request(inputs)

        if use_scheduler:
            if not self._scheduler:
                raise ValueError('Scheduler is not set')

            schedule = self._scheduler.schedule(batch_request)
            outputs = []

            async for batch_result in self._scheduler.execute(schedule):
                outputs.extend(self._batch_result_to_outputs(batch_result))

        else:
            batch_result = await self._em.batch_embed(batch_request)
            outputs = self._batch_result_to_outputs(batch_result)

        return outputs

    async def batch_assist_init(self, inputs: list[EmbedantInputType]) -> str:
        batch_request = self._inputs_to_batch_request(inputs)
        batch_id = await self._em.batch_embed_init(batch_request)

        return batch_id

    async def batch_assist_result(
        self, batch_id: str, batch_request_id: UUID
    ) -> list[EmbedantOutputType] | None:
        batch_result = await self._em.batch_embed_result(batch_id, batch_request_id)

        if batch_result is None:
            return

        outputs = self._batch_result_to_outputs(batch_result)

        return outputs
