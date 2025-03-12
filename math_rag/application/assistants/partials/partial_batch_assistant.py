from typing import cast

from math_rag.application.base.assistants import (
    BaseAssistantProtocol,
    BaseBatchAssistant,
)
from math_rag.application.base.inference import BaseBatchLLM
from math_rag.application.base.repositories.documents import (
    BaseLLMFailedRequestRepository,
)
from math_rag.application.models.inference import LLMRequestBatch
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
        llm: BaseBatchLLM,
        failed_request_repository: BaseLLMFailedRequestRepository,
    ):
        self.llm = llm
        self.failed_request_repository = failed_request_repository

        args = TypeUtil.get_type_args(self.__class__)
        self.response_type = cast(type[AssistantOutputType], args[0][1])

    async def batch_assist(
        self,
        inputs: list[AssistantInputType],
        response_type: type[AssistantOutputType],
    ) -> list[AssistantOutputType]:
        request_batch = LLMRequestBatch(
            requests=[self.encode_to_request(input) for input in inputs]
        )
        response_bundle = await self.llm.batch_generate(
            request_batch, response_type, poll_interval=..., num_retries=...
        )

        if response_bundle.failed_requests:
            await self.failed_request_repository.insert_many(
                response_bundle.failed_requests
            )

        outputs = [
            self.decode_from_response_list(response_list)
            for response_list in response_bundle.response_lists
        ]

        return outputs

    async def batch_assist_init(self, inputs: list[AssistantInputType]) -> str:
        request_batch = LLMRequestBatch(
            requests=[self.encode_to_request(input) for input in inputs]
        )
        batch_id = await self.llm.batch_generate_init(request_batch)

        return batch_id

    async def batch_assist_result(
        self,
        batch_id: str,
    ) -> list[AssistantOutputType] | None:
        response_batch = await self.llm.batch_generate_result(
            batch_id, self.response_type
        )

        if response_batch is None:
            return

        outputs = [
            self.decode_from_response_list(response_list)
            for response_list in response_batch.response_lists
        ]

        return outputs
