import asyncio
import json
import logging

from backoff import expo, on_exception
from openai import AsyncOpenAI, RateLimitError
from openai.types.chat import ChatCompletion

from math_rag.application.base.inference import BaseLLM
from math_rag.application.models import (
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
    async def generate_text(self, request: LLMRequest) -> list[LLMResponse[str]]:
        params = request.params
        messages = request.conversation.messages
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
        content = completion.choices[0].message.content

        return LLMResponse(content=content)

    @retry
    async def generate_json(
        self,
        request: LLMRequest,
    ) -> list[LLMResponse[LLMResponseType]]:
        params = request.params
        messages = request.conversation.messages
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
        content = completion.choices[0].message.parsed

        return LLMResponse(content=content)

    async def batch_generate_text(
        self, request_batch: LLMRequestBatch
    ) -> tuple[LLMRequestBatch, list[LLMResponse[str]]]:
        url = '/v1/chat/completions'
        custom_id_to_request: dict[str, LLMRequest] = {}
        openai_requests = []

        for i, request in enumerate(request_batch.requests):
            custom_id = str(i)
            custom_id_to_request[custom_id] = request
            params = request.params
            openai_request = {
                'custom_id': custom_id,
                'method': 'POST',
                'url': url,
                'body': {
                    'model': params.model,
                    'messages': [
                        {'role': message.role, 'content': message.content}
                        for message in request.conversation.messages
                    ],
                    'response_format': {'type': 'text'},
                    'temperature': params.temperature,
                    'logprobs': params.logprobs,
                    'top_logprobs': params.top_logprobs,
                },
            }
            openai_requests.append(openai_request)

        jsonl_str = '\n'.join(
            json.dumps(openai_request, separators=(',', ':'))
            for openai_request in openai_requests
        )
        jsonl_bytes = jsonl_str.encode('utf-8')

        input_file = await self.client.files.create(file=jsonl_bytes, purpose='batch')
        batch = await self.client.batches.create(
            input_file_id=input_file.id,
            endpoint=url,
            completion_window='24h',
            metadata=None,
        )
        prev_status = batch.status
        logging.info(f'Batch {batch.id} created with status {batch.status}')

        while True:
            batch = await self.client.batches.retrieve(batch.id)

            if batch.status != prev_status:
                prev_status = batch.status
                logging.info(f'Batch {batch.id} status updated to {batch.status}')

            match batch.status:
                case 'validating' | 'in_progress' | 'finalizing' | 'cancelling':
                    await asyncio.sleep(5 * 60)

                case 'failed':
                    raise ValueError(f'File {input_file.id} validation failed')

                case 'completed' | 'expired' | 'cancelled':
                    break

        response_content = await self.client.files.content(batch.output_file_id)
        lines = response_content.text.strip().splitlines()
        incomplete_requests, responses = [], []

        for line in lines:
            data = json.loads(line)
            response = data['response']

            if response is None:
                custom_id = data['custom_id']
                incomplete_request = custom_id_to_request[custom_id]
                incomplete_requests.append(incomplete_request)

            else:
                completion = ChatCompletion(**response['body'])
                content = completion.choices[0].message.content
                response = LLMResponse(content=content)
                responses.append(response)

        await self.client.files.delete(input_file.id), responses

        return LLMRequestBatch(requests=incomplete_requests)

    async def batch_generate_text_init(self, prompts: list[str], params: LLMParams):
        # TODO create batch
        pass

    async def batch_generate_text_result(
        self, prompts: list[str], params: LLMParams
    ) -> tuple[list[str], list[str]] | None:
        # TODO check if everything is completed, return None if its not
        pass
