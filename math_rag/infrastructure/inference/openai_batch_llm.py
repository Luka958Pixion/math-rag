import json
import logging

from asyncio import sleep
from uuid import UUID

from openai import NOT_GIVEN, AsyncOpenAI
from openai.types.chat import ChatCompletion

from math_rag.application.base.inference import BaseBatchLLM
from math_rag.application.models.inference import (
    LLMFailedRequest,
    LLMRequestBatch,
    LLMResponseBatchBundle,
    LLMResponseList,
)
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.mappings.inference import (
    LLMErrorMapping,
    LLMRequestMapping,
    LLMResponseListMapping,
)


class OpenAIBatchLLM(BaseBatchLLM):
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    async def _batch_generate(
        self,
        request_batch: LLMRequestBatch[LLMResponseType],
        response_type: type[LLMResponseType],
        poll_interval: float,
    ) -> LLMResponseBatchBundle[LLMResponseType]:
        batch_id = await self.batch_generate_init(request_batch)

        while True:
            response_bundle = await self.batch_generate_result(batch_id, response_type)

            if response_bundle is not None:
                return response_bundle

            await sleep(poll_interval)

    async def _batch_generate_retry(
        self,
        request_batch: LLMRequestBatch[LLMResponseType],
        response_type: type[LLMResponseType],
        *,
        poll_interval: float,
        max_num_retries: int,
    ) -> LLMResponseBatchBundle[LLMResponseType]:
        if max_num_retries < 0:
            raise ValueError()

        num_total = len(request_batch.requests)
        response_lists: list[LLMResponseList[LLMResponseType]] = []

        for _ in range(max_num_retries + 1):
            response_bundle = await self._batch_generate(
                request_batch, response_type, poll_interval
            )
            response_lists.extend(response_bundle.response_lists)

            if not response_bundle.failed_requests:
                break

            request_batch = LLMRequestBatch(
                requests=[
                    failed_request.request
                    for failed_request in response_bundle.failed_requests
                ]
            )

        response_bundle.response_lists = response_lists
        num_completed = len(response_lists)

        logging.info(
            f'Completed {num_completed}/{num_total} requests within {max_num_retries} retries'
        )

        return response_bundle

    async def batch_generate(
        self,
        request_batch: LLMRequestBatch[LLMResponseType],
        response_type: type[LLMResponseType],
        *,
        poll_interval: float,
        num_retries: int,
    ) -> LLMResponseBatchBundle[LLMResponseType]:
        if num_retries:
            response_bundle = await self._batch_generate_retry(
                request_batch,
                response_type,
                poll_interval=poll_interval,
                max_num_retries=num_retries,
            )

        response_bundle = await self._batch_generate(
            request_batch, response_type, poll_interval
        )

        return response_bundle

    async def batch_generate_init(
        self,
        request_batch: LLMRequestBatch[LLMResponseType],
    ) -> str:
        url = '/v1/chat/completions'
        requests = [
            {
                'custom_id': str(request.id),
                'method': 'POST',
                'url': url,
                'body': LLMRequestMapping[LLMResponseType].to_target(
                    request, use_parsed=True
                ),
            }
            for request in request_batch.requests
        ]

        lines = [json.dumps(request, separators=(',', ':')) for request in requests]
        jsonl_str = '\n'.join(lines)
        jsonl_bytes = jsonl_str.encode('utf-8')

        input_file = await self.client.files.create(file=jsonl_bytes, purpose='batch')
        batch = await self.client.batches.create(
            input_file_id=input_file.id,
            endpoint=url,
            completion_window='24h',
            metadata=None,
        )
        logging.info(f'Batch {batch.id} created with status {batch.status}')

        return batch.id

    async def batch_generate_result(
        self, batch_id: str, response_type: type[LLMResponseType]
    ) -> LLMResponseBatchBundle[LLMResponseType] | None:
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
                data['body']
            )
            for data in input_items
        }

        failed_requests: list[LLMFailedRequest[LLMResponseType]] = []
        response_lists: list[LLMResponseList[LLMResponseType]] = []

        for data in output_items:
            request_id = UUID(data['custom_id'])
            response = data['response']

            if response is None:
                if 'error' in data:
                    error = LLMErrorMapping.to_source(data['error'])
                    failed_request = LLMFailedRequest(
                        request=requests_dict[request_id],
                        errors=[error],
                    )
                    failed_requests.append(failed_request)

            else:
                completion = ChatCompletion(**response['body'])
                response_list = LLMResponseListMapping[LLMResponseType].to_source(
                    completion, request_id=request_id, response_type=response_type
                )
                response_lists.append(response_list)

        await self.client.files.delete(batch.input_file_id)
        await self.client.files.delete(batch.output_file_id)

        response_bundle = LLMResponseBatchBundle(
            response_lists=response_lists, failed_requests=failed_requests
        )

        return response_bundle
