import asyncio
import json
import logging

from backoff import expo, on_exception
from openai import AsyncOpenAI, RateLimitError
from openai.types.chat import ChatCompletion

from math_rag.application.base.inference import BaseLLM, T
from math_rag.application.models import LLMMessage, LLMParams, LLMResponse


retry = on_exception(expo, RateLimitError, max_time=60, max_tries=6)


class LLM(BaseLLM):
    def __init__(self, client: AsyncOpenAI):
        self.client = client

    @retry
    async def generate_text(
        self, messages: list[LLMMessage], params: LLMParams
    ) -> list[LLMResponse[str]]:
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
        messages: list[LLMMessage],
        params: LLMParams,
        response_model_type: type[T],
    ) -> list[LLMResponse[T]]:
        completion = await self.client.beta.chat.completions.parse(
            model=params.model,
            messages=[
                {'role': message.role, 'content': message.content}
                for message in messages
            ],
            response_format=response_model_type,
            temperature=params.temperature,
            logprobs=params.logprobs,
            top_logprobs=params.top_logprobs,
        )
        content = completion.choices[0].message.parsed

        return LLMResponse(content=content)

    async def batch_generate_text(
        self, prompts: list[str], params: LLMParams
    ) -> tuple[list[str], list[str]]:
        url = '/v1/chat/completions'
        custom_id_to_prompt: dict[str, str] = {}
        requests = []

        for i, prompt in enumerate(prompts):
            custom_id = str(i)
            custom_id_to_prompt[custom_id] = prompt
            request = {
                'custom_id': custom_id,
                'method': 'POST',
                'url': url,
                'body': {
                    'model': params.model,
                    'messages': [{'role': 'user', 'content': prompt}],
                    'response_format': {'type': 'text'},
                    'temperature': params.temperature,
                    'logprobs': params.logprobs,
                    'top_logprobs': params.top_logprobs,
                },
            }
            requests.append(request)

        jsonl_str = '\n'.join(
            json.dumps(request, separators=(',', ':')) for request in requests
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
        results, prompts = [], []

        for line in lines:
            data = json.loads(line)
            response = data['response']

            if response is None:
                custom_id = data['custom_id']
                prompt = custom_id_to_prompt[custom_id]
                prompts.append(prompt)

            else:
                completion = ChatCompletion(**response['body'])
                result = completion.choices[0].message.content
                results.append(result)

        await self.client.files.delete(input_file.id)

        return results, prompts

    async def batch_generate_text_init(self, prompts: list[str], params: LLMParams):
        # TODO create batch
        pass

    async def batch_generate_text_result(
        self, prompts: list[str], params: LLMParams
    ) -> tuple[list[str], list[str]] | None:
        # TODO check if everything is completed, return None if its not
        pass
