import json
import logging

from asyncio import sleep

from openai import NOT_GIVEN, AsyncOpenAI
from openai.lib._parsing._completions import (
    parse_chat_completion,
    type_to_response_format_param,
)
from openai.types.chat import ChatCompletion

from math_rag.application.base.inference import BaseBatchLLM
from math_rag.application.models.inference import (
    LLMConversation,
    LLMError,
    LLMMessage,
    LLMParams,
    LLMRequest,
    LLMRequestBatch,
    LLMResponseBatch,
    LLMResponseImmediateBatch,
    LLMResponseList,
    LLMTextResponse,
)
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.mappings.inference import LLMResponseListMapping


class OpenAIBatchLLM(BaseBatchLLM):
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    async def batch_generate(
        self,
        request_batch: LLMRequestBatch[LLMResponseType],
        response_type: type[LLMResponseType],
        poll_interval: float,
    ) -> LLMResponseBatch[LLMResponseType]:
        batch_id = await self.batch_generate_init(request_batch)

        while True:
            result = await self.batch_generate_result(batch_id, response_type)

            if result is not None:
                return result

            await sleep(poll_interval)

    async def batch_generate_retry(
        self,
        request_batch: LLMRequestBatch[LLMResponseType],
        response_type: type[LLMResponseType],
        poll_interval: float,
        num_retries: int,
    ) -> LLMResponseBatch[LLMResponseType]:
        if num_retries < 0:
            raise ValueError()

        num_total = len(request_batch.requests)
        response_lists: list[LLMResponseList[LLMResponseType]] = []

        for _ in range(num_retries + 1):
            response_batch = await self.batch_generate(
                request_batch, response_type, poll_interval
            )
            response_lists.extend(response_batch.response_lists)

            if not response_batch.incomplete_request_batch.requests:
                break

            request_batch = response_batch.incomplete_request_batch

        response_batch.response_lists = response_lists
        num_completed = len(response_lists)

        logging.info(
            f'{self.batch_generate_retry.__name__} completed {num_completed}/{num_total} requests within {num_retries} retries'
        )

        return response_batch

    async def batch_generate_init(
        self,
        request_batch: LLMRequestBatch[LLMResponseType],
        response_type: type[LLMResponseType],
    ) -> str:
        url = '/v1/chat/completions'
        response_format = (
            {'type': 'text'}
            if response_type is LLMTextResponse
            else type_to_response_format_param(response_format)
        )
        requests = [
            {
                'custom_id': str(request.id),
                'method': 'POST',
                'url': url,
                'body': {
                    'model': request.params.model,
                    'messages': [
                        {'role': message.role, 'content': message.content}
                        for message in request.conversation.messages
                    ],
                    'response_format': response_format,
                    'temperature': request.params.temperature,
                    'logprobs': request.params.top_logprobs is not None,
                    'top_logprobs': request.params.top_logprobs,
                    'max_completion_tokens': request.params.max_completion_tokens,
                },
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
    ) -> LLMResponseBatch[LLMResponseType] | None:
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

            case 'failed':
                raise ValueError(f'File {batch.input_file_id} validation failed')

            case 'completed' | 'expired' | 'cancelled':
                pass

        output_file_content = await self.client.files.content(batch.output_file_id)
        lines = output_file_content.text.strip().splitlines()
        complete_request_ids = []
        incomplete_request_ids = []
        request_id_to_response_list: dict[str, LLMResponseList[LLMResponseType]] = {}

        for line in lines:
            data = json.loads(line)
            response = data['response']
            custom_id = str(data['custom_id'])

            if response is None:
                incomplete_request_ids.append(custom_id)

                if 'error' in data:
                    error = LLMError(
                        message=data['error']['message']
                        if 'message' in data['error']
                        else str(),
                        body=data['error']['body'] if 'body' in data['error'] else None,
                    )
                    # TODO save error

            else:
                completion = ChatCompletion(**response['body'])

                if response_type is LLMTextResponse:
                    response_list = LLMResponseListMapping[LLMResponseType].to_source(
                        completion
                    )

                else:
                    parsed_completion = parse_chat_completion(
                        response_format=response_type,
                        input_tools=NOT_GIVEN,
                        chat_completion=completion,
                    )
                    response_list = LLMResponseListMapping[LLMResponseType].to_source(
                        parsed_completion
                    )

                request_id_to_response_list[custom_id] = response_list
                complete_request_ids.append(custom_id)

        response_lists = [
            request_id_to_response_list[request_id]
            for request_id in complete_request_ids
        ]

        input_file_content = await self.client.files.content(batch.input_file_id)
        lines = input_file_content.text.strip().splitlines()
        incomplete_requests: list[LLMRequest[LLMResponseType]] = []

        for line in lines:
            data = json.loads(line)
            request_id = str(data['custom_id'])

            if request_id not in incomplete_request_ids:
                continue

            body = data['body']
            messages = body['messages']

            request = LLMRequest(
                conversation=LLMConversation(
                    messages=[
                        LLMMessage(role=message['role'], content=message['content'])
                        for message in messages
                    ]
                ),
                params=LLMParams[LLMResponseType](
                    model=body['messages'],
                    temperature=body['temperature'],
                    logprobs=body['logprobs'],
                    top_logprobs=body['top_logprobs'],
                    response_type=response_type,
                    max_completion_tokens=body['max_completion_tokens'],
                    n=body['n'],
                ),
            )
            incomplete_requests.append(request)

        await self.client.files.delete(batch.input_file_id)
        await self.client.files.delete(batch.output_file_id)

        incomplete_request_batch = LLMRequestBatch(requests=incomplete_requests)
        response_batch = LLMResponseBatch(
            incomplete_request_batch=incomplete_request_batch,
            response_lists=response_lists,
        )

        return response_batch
