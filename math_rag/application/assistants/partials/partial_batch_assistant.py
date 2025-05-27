from typing import cast
from uuid import UUID

from math_rag.application.base.assistants import (
    BaseAssistantProtocol,
    BaseBatchAssistant,
)
from math_rag.application.base.inference import (
    BaseBatchLLMRequestManagedScheduler,
    BaseBatchManagedLLM,
)
from math_rag.application.models.inference import LLMBatchRequest, LLMBatchResult
from math_rag.application.types.assistants import (
    AssistantInputType,
    AssistantOutputType,
)
from math_rag.shared.utils import TypeUtil


class PartialBatchAssistant(
    BaseBatchAssistant[AssistantInputType, AssistantOutputType],
    BaseAssistantProtocol[AssistantInputType, AssistantOutputType],
):
    def __init__(
        self,
        llm: BaseBatchManagedLLM,
        scheduler: BaseBatchLLMRequestManagedScheduler | None,
    ):
        self._llm = llm
        self._scheduler = scheduler

        args = TypeUtil.get_type_args(self.__class__)
        self._response_type = cast(type[AssistantOutputType], args[0][1])

    def _inputs_to_batch_request(
        self, inputs: list[AssistantInputType]
    ) -> LLMBatchRequest[AssistantOutputType]:
        return LLMBatchRequest(requests=[self.encode_to_request(input) for input in inputs])

    def _batch_result_to_outputs(
        self, batch_result: LLMBatchResult[AssistantOutputType]
    ) -> list[AssistantOutputType]:
        # map BoundAssistantOutput to AssistantOutput
        for response_list in batch_result.response_lists:
            for response in response_list.responses:
                content_dict = response.content.model_dump(exclude_unset=True)
                response.content = self._response_type(**content_dict)

        return [
            self.decode_from_response_list(response_list)
            for response_list in batch_result.response_lists
        ]

    async def batch_assist(
        self, inputs: list[AssistantInputType], *, use_scheduler: bool
    ) -> list[AssistantOutputType]:
        batch_request = self._inputs_to_batch_request(inputs)

        if use_scheduler:
            if not self._scheduler:
                raise ValueError('Scheduler is not set')

            schedule = self._scheduler.schedule(batch_request)
            outputs = []

            async for batch_result in self._scheduler.execute(schedule, self._response_type):
                outputs.extend(self._batch_result_to_outputs(batch_result))

        else:
            batch_result = await self._llm.batch_generate(batch_request, self._response_type)
            outputs = self._batch_result_to_outputs(batch_result)

        return outputs

    async def batch_assist_init(self, inputs: list[AssistantInputType]) -> str:
        batch_request = self._inputs_to_batch_request(inputs)
        batch_id = await self._llm.batch_generate_init(batch_request)

        return batch_id

    async def batch_assist_result(
        self, batch_id: str, batch_request_id: UUID
    ) -> list[AssistantOutputType] | None:
        batch_result = await self._llm.batch_generate_result(
            batch_id,
            batch_request_id,
            self._response_type,
        )

        if batch_result is None:
            return

        outputs = self._batch_result_to_outputs(batch_result)

        return outputs
