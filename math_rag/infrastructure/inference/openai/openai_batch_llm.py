import json
import logging

from uuid import UUID

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletion

from math_rag.application.models.inference import (
    LLMBatchRequest,
    LLMBatchResult,
    LLMFailedRequest,
    LLMRequest,
    LLMResponseList,
)
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.inference.partials import PartialBatchLLM
from math_rag.infrastructure.mappings.inference.openai import (
    LLMErrorMapping,
    LLMRequestMapping,
    LLMResponseListMapping,
)


class OpenAIBatchLLM(PartialBatchLLM):
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    async def batch_generate_init(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
    ) -> str:
        url = '/v1/chat/completions'
        request_dicts = [
            {
                'custom_id': str(request.id),
                'method': 'POST',
                'url': url,
                'body': LLMRequestMapping[LLMResponseType].to_target(
                    request, use_parsed=True
                ),
            }
            for request in batch_request.requests
        ]

        lines = [
            json.dumps(request_dict, separators=(',', ':'))
            for request_dict in request_dicts
        ]
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

        requests_dict: dict[UUID, LLMRequest[LLMResponseType]] = {}

        for data in input_items:
            request_id = UUID(data['custom_id'])
            request = LLMRequestMapping[LLMResponseType].to_source(
                data['body'],
                request_id=request_id,
                response_type=response_type,
            )

            requests_dict[request_id] = request

        failed_requests: list[LLMFailedRequest[LLMResponseType]] = []
        response_lists: list[LLMResponseList[LLMResponseType]] = []

        for data in output_items:
            request_id = UUID(data['custom_id'])
            request = requests_dict[request_id]
            response = data['response']

            if response is None:
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

        await self.client.files.delete(batch.input_file_id)
        await self.client.files.delete(batch.output_file_id)

        return batch_result
