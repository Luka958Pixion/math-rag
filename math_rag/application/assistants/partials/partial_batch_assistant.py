from typing import cast

from math_rag.application.base.assistants import (
    BaseAssistantProtocol,
    BaseBatchAssistant,
)
from math_rag.application.base.inference import BaseBatchLLM
from math_rag.application.base.repositories.documents import (
    BaseLLMFailedRequestRepository,
)
from math_rag.application.base.services import BaseSettingsLoaderService
from math_rag.application.models.inference import LLMBatchRequest
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
        settings_loader_service: BaseSettingsLoaderService,
        failed_request_repository: BaseLLMFailedRequestRepository,
    ):
        self.llm = llm
        self.settings_loader_service = settings_loader_service
        self.failed_request_repository = failed_request_repository

        args = TypeUtil.get_type_args(self.__class__)
        self.response_type = cast(type[AssistantOutputType], args[0][1])

    async def batch_assist(
        self,
        inputs: list[AssistantInputType],
        response_type: type[AssistantOutputType],
    ) -> list[AssistantOutputType]:
        batch_request = LLMBatchRequest(
            requests=[self.encode_to_request(input) for input in inputs]
        )
        settings = self.settings_loader_service.load_batch_llm_settings()
        batch_result = await self.llm.batch_generate(
            batch_request,
            response_type,
            poll_interval=settings.poll_interval,
            max_num_retries=settings.max_num_retries,
        )

        if batch_result.failed_requests:
            await self.failed_request_repository.insert_many(
                batch_result.failed_requests
            )

        outputs = [
            self.decode_from_response_list(response_list)
            for response_list in batch_result.response_lists
        ]

        return outputs

    async def batch_assist_init(self, inputs: list[AssistantInputType]) -> str:
        batch_request = LLMBatchRequest(
            requests=[self.encode_to_request(input) for input in inputs]
        )
        batch_id = await self.llm.batch_generate_init(batch_request)

        return batch_id

    async def batch_assist_result(
        self,
        batch_id: str,
    ) -> list[AssistantOutputType] | None:
        batch_result = await self.llm.batch_generate_result(
            batch_id, self.response_type
        )

        if batch_result is None:
            return

        outputs = [
            self.decode_from_response_list(response_list)
            for response_list in batch_result.response_lists
        ]

        return outputs
