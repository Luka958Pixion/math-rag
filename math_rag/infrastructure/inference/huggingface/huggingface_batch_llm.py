import json
import logging

from asyncio import sleep
from uuid import UUID

from math_rag.application.base.inference import BaseBatchLLM
from math_rag.application.models.inference import (
    LLMBatchRequest,
    LLMBatchResult,
    LLMFailedRequest,
    LLMResponseList,
)
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.clients import HPCClient, PBSProClient, SFTPClient
from math_rag.infrastructure.mappings.inference.huggingface import (
    LLMErrorMapping,
    LLMRequestMapping,
    LLMResponseListMapping,
)
from math_rag.infrastructure.utils import BytesStreamerUtil


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
            LLMRequestMapping.to_target(request) for request in batch_request.requests
        ]

        lines = [json.dumps(request, separators=(',', ':')) for request in requests]
        jsonl_str = '\n'.join(lines)
        jsonl_bytes = jsonl_str.encode('utf-8')
        source = BytesStreamerUtil.stream_bytes(jsonl_bytes)

        await self.sftp_client.upload(source)

        pbs_path = ...
        job_id = await self.pbs_pro_client.queue_submit(pbs_path)
        status = await self.pbs_pro_client.queue_status(job_id)

        logging.info(f'Batch job {job_id} created with state {status.state}')

        return job_id

    async def batch_generate_result(
        self, batch_id: str, response_type: type[LLMResponseType]
    ) -> LLMBatchResult[LLMResponseType] | None:
        batch = await self.client.batches.retrieve(batch_id)

        logging.info(
            f'Batch {batch.id} status {batch.status}\n'
            f'Batch {batch.id} requests - '
            f'completed: {batch.request_counts.completed}, '
            f'failed: {batch.request_counts.failed}, '
            f'total: {batch.request_counts.total}'
        )

        match batch.status:
            case 'validating' | 'in_progress' | 'finalizing' | 'cancelling':
                return None

            case 'completed' | 'expired' | 'cancelled':
                pass

            case 'failed':
                raise ValueError(f'File {batch.input_file_id} validation failed')

        input_file_content = await self.client.files.content(batch.input_file_id)
        output_file_content = await self.client.files.content(batch.output_file_id)

        input_lines = input_file_content.text.strip().splitlines()
        output_lines = output_file_content.text.strip().splitlines()

        input_items = [json.loads(line) for line in input_lines]
        output_items = [json.loads(line) for line in output_lines]

        requests_dict = {
            UUID(data['custom_id']): LLMRequestMapping[LLMResponseType].to_source(
                data['body'],
                request_id=UUID(data['custom_id']),
                response_type=response_type,
            )
            for data in input_items
        }

        failed_requests: list[LLMFailedRequest[LLMResponseType]] = []
        response_lists: list[LLMResponseList[LLMResponseType]] = []

        for data in output_items:
            request_id = UUID(data['custom_id'])
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
                completion = ChatCompletion(**response['body'])
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
