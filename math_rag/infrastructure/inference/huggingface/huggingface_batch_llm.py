import json
import logging

from asyncio import sleep
from pathlib import Path
from uuid import UUID

from huggingface_hub.inference._generated.types import ChatCompletionOutput

from math_rag.application.base.inference import BaseBatchLLM
from math_rag.application.models.inference import (
    LLMBatchRequest,
    LLMBatchResult,
    LLMFailedRequest,
    LLMRequest,
    LLMResponseList,
)
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.clients import HPCClient, PBSProClient, SFTPClient
from math_rag.infrastructure.enums.hpc.pbs import PBSProJobState
from math_rag.infrastructure.mappings.inference.huggingface import (
    LLMErrorMapping,
    LLMRequestMapping,
    LLMResponseListMapping,
)
from math_rag.infrastructure.utils import BytesStreamerUtil, FileStreamerUtil


class HuggingFaceBatchLLM(BaseBatchLLM):
    def __init__(
        self,
        hpc_client: HPCClient,
        pbs_pro_client: PBSProClient,
        sftp_client: SFTPClient,
    ):
        self.hpc_client = hpc_client
        self.pbs_pro_client = pbs_pro_client
        self.sftp_client = sftp_client

    async def _batch_generate(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
        response_type: type[LLMResponseType],
        poll_interval: float,
    ) -> LLMBatchResult[LLMResponseType]:
        batch_id = await self.batch_generate_init(batch_request)

        while True:
            batch_result = await self.batch_generate_result(batch_id, response_type)

            if batch_result is not None:
                return batch_result

            await sleep(poll_interval)

    async def _batch_generate_retry(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
        response_type: type[LLMResponseType],
        *,
        poll_interval: float,
        max_num_retries: int,
    ) -> LLMBatchResult[LLMResponseType]:
        if max_num_retries < 0:
            raise ValueError()

        num_total = len(batch_request.requests)
        response_lists: list[LLMResponseList[LLMResponseType]] = []

        for _ in range(max_num_retries + 1):
            batch_result = await self._batch_generate(
                batch_request, response_type, poll_interval
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

        logging.info(
            f'Completed {num_completed}/{num_total} requests within {max_num_retries} retries'
        )

        return batch_result

    async def batch_generate(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
        response_type: type[LLMResponseType],
        *,
        poll_interval: float,
        num_retries: int,
    ) -> LLMBatchResult[LLMResponseType]:
        if num_retries:
            batch_result = await self._batch_generate_retry(
                batch_request,
                response_type,
                poll_interval=poll_interval,
                max_num_retries=num_retries,
            )

        batch_result = await self._batch_generate(
            batch_request, response_type, poll_interval
        )

        return batch_result

    async def batch_generate_init(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
    ) -> str:
        requests = [
            {
                'request_id': str(request.id),
                'request': LLMRequestMapping[LLMResponseType].to_target(request),
            }
            for request in batch_request.requests
        ]
        lines = [json.dumps(request, separators=(',', ':')) for request in requests]
        jsonl_str = '\n'.join(lines)
        jsonl_bytes = jsonl_str.encode('utf-8')
        source = BytesStreamerUtil.stream_bytes(jsonl_bytes)

        await self.sftp_client.upload(source)

        pbs_path = ...  # TODO
        batch_id = await self.pbs_pro_client.queue_submit(pbs_path)
        status = await self.pbs_pro_client.queue_status(batch_id)

        logging.info(f'Batch {batch_id} created with state {status.state}')

        return batch_id

    async def batch_generate_result(
        self, batch_id: str, response_type: type[LLMResponseType]
    ) -> LLMBatchResult[LLMResponseType] | None:
        status = await self.pbs_pro_client.queue_status(batch_id)

        logging.info(f'Batch {batch_id} state {status.state}')

        match status.state:
            case (
                PBSProJobState.BEGUN
                | PBSProJobState.QUEUED
                | PBSProJobState.RUNNING
                | PBSProJobState.EXITING
                | PBSProJobState.WAITING
                | PBSProJobState.TRANSITING
                | PBSProJobState.SUSPENDED
                | PBSProJobState.USER_SUSPENDED
                | PBSProJobState.HELD
                | PBSProJobState.MOVED
            ):
                return None

            case PBSProJobState.FINISHED | PBSProJobState.EXITED:
                pass

        input_path = Path(...)
        output_path = Path(...)
        input_file_stream = await self.sftp_client.download(input_path, None)
        output_file_stream = await self.sftp_client.download(output_path, None)
        input_stream = FileStreamerUtil.read_jsonl_file_stream(input_file_stream)
        output_stream = FileStreamerUtil.read_jsonl_file_stream(output_file_stream)

        requests_dict: dict[UUID, LLMRequest[LLMResponseType]] = {}

        async for data in input_stream:
            request_id = UUID(data['extra_body']['request_id'])
            request = LLMRequestMapping[LLMResponseType].to_source(
                data['body'],
                request_id=request_id,
                response_type=response_type,
            )

            requests_dict[request_id] = request

        failed_requests: list[LLMFailedRequest[LLMResponseType]] = []
        response_lists: list[LLMResponseList[LLMResponseType]] = []

        async for data in output_stream:
            request_id = UUID(data['request_id'])
            request = requests_dict[request_id]
            response = data['response']

            if response is None:
                if 'error' in data:
                    error = LLMErrorMapping.to_source(data['error'])
                    failed_request = LLMFailedRequest(
                        request=request,
                        errors=[error],
                    )
                    failed_requests.append(failed_request)

            else:
                completion = ChatCompletionOutput(**response)
                response_list = LLMResponseListMapping[LLMResponseType].to_source(
                    completion,
                    request_id=request_id,
                    input_id=request.params.metadata['input_id'],
                    response_type=response_type,
                )
                response_lists.append(response_list)

        batch_result = LLMBatchResult(
            response_lists=response_lists, failed_requests=failed_requests
        )

        return batch_result
