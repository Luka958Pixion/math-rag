import asyncio
import json
import logging

from typing import Type

from backoff import expo, on_exception
from openai import AsyncOpenAI, RateLimitError
from openai.types.chat import ChatCompletion

from math_rag.application.base.inference import BaseLLM
from math_rag.application.models import (
    LLMConversation,
    LLMMessage,
    LLMParams,
    LLMRequest,
    LLMRequestBatch,
    LLMResponse,
)
from math_rag.application.types import LLMResponseType


retry = on_exception(expo, RateLimitError, max_time=60, max_tries=6)


class LLM(BaseLLM):
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    @retry
    async def generate(
        self,
        request: LLMRequest[LLMResponseType],
    ) -> list[LLMResponse[LLMResponseType]]:
        params = request.params
        messages = request.conversation.messages

        if params.response_type is str:
            completion = await self.client.chat.completions.create(
                model=params.model,
                messages=[
                    {'role': message.role, 'content': message.content}
                    for message in messages
                ],
                response_format={'type': 'text'},
                temperature=params.temperature,
                logprobs=params.logprobs,
                top_logprobs=params.top_logprobs,
            )
            responses = [
                LLMResponse(content=choice.message.content)
                for choice in completion.choices
            ]

        else:
            completion = await self.client.beta.chat.completions.parse(
                model=params.model,
                messages=[
                    {'role': message.role, 'content': message.content}
                    for message in messages
                ],
                response_format=params.response_type,
                temperature=params.temperature,
                logprobs=params.logprobs,
                top_logprobs=params.top_logprobs,
            )
            responses = [
                LLMResponse(content=choice.message.parsed)
                for choice in completion.choices
            ]

        return responses

    async def batch_generate(
        self,
        request_batch: LLMRequestBatch[LLMResponseType],
        response_type: Type[LLMResponseType],
    ) -> tuple[list[LLMResponse[LLMResponseType]], LLMRequestBatch[LLMResponseType]]:
        batch_id = await self.batch_generate_init(request_batch)

        while True:
            result = await self.batch_generate_result(batch_id, response_type)

            if result is not None:
                return result

            await asyncio.sleep(5 * 60)

    async def batch_generate_init(
        self, request_batch: LLMRequestBatch[LLMResponseType]
    ) -> str:
        url = '/v1/chat/completions'
        requests = [
            {
                'custom_id': str(i),
                'method': 'POST',
                'url': url,
                'body': {
                    'model': request.params.model,
                    'messages': [
                        {'role': message.role, 'content': message.content}
                        for message in request.conversation.messages
                    ],
                    'response_format': {'type': 'text'},
                    'temperature': request.params.temperature,
                    'logprobs': request.params.logprobs,
                    'top_logprobs': request.params.top_logprobs,
                },
            }
            for i, request in enumerate(request_batch.requests)
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
        self, batch_id: str, response_type: Type[LLMResponseType]
    ) -> (
        tuple[list[LLMResponse[LLMResponseType]], LLMRequestBatch[LLMResponseType]]
        | None
    ):
        batch = await self.client.batches.retrieve(batch_id)

        if batch.status != prev_status:
            prev_status = batch.status
            logging.info(f'Batch {batch.id} status updated to {batch.status}')

        match batch.status:
            case 'validating' | 'in_progress' | 'finalizing' | 'cancelling':
                return None

            case 'failed':
                raise ValueError(f'File {batch.input_file_id} validation failed')

            case 'completed' | 'expired' | 'cancelled':
                pass

        output_file_content = await self.client.files.content(batch.output_file_id)
        lines = output_file_content.text.strip().splitlines()
        incomplete_request_ids = []
        responses = []

        for line in lines:
            data = json.loads(line)
            response = data['response']

            if response is None:
                custom_id = data['custom_id']
                incomplete_request_ids.append(custom_id)

            else:
                completion = ChatCompletion(**response['body'])
                content = completion.choices[0].message.content
                response = LLMResponse[response_type](content=content)
                responses.append(response)

        input_file_content = await self.client.files.content(batch.input_file_id)
        lines = input_file_content.text.strip().splitlines()
        incomplete_requests = []

        for line in lines:
            data = json.loads(line)
            request_id = data['custom_id']

            if request_id not in incomplete_request_ids:
                continue

            body = data['body']
            messages = body['messages']

            request = LLMRequest[response_type](
                conversation=LLMConversation(
                    messages=[
                        LLMMessage(role=message['role'], content=message['content'])
                        for message in messages
                    ]
                ),
                params=LLMParams[response_type](
                    model=body['messages'],
                    temperature=body['messages'],
                    logprobs=body['messages'],
                    top_logprobs=body['messages'],
                    response_type=response_type,
                    n=body['messages'],
                ),
            )
            incomplete_requests.append(request)

        incomplete_request_batch = LLMRequestBatch[response_type](
            requests=incomplete_requests
        )

        await self.client.files.delete(batch.input_file_id)
        await self.client.files.delete(batch.output_file_id)

        return responses, incomplete_request_batch
