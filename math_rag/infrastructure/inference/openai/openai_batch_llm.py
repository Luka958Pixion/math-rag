import json

from asyncio import sleep
from logging import getLogger
from uuid import UUID

from openai import AsyncOpenAI, BadRequestError
from openai.types.chat import ChatCompletion

from math_rag.application.models.inference import (
    LLMBatchRequest,
    LLMBatchResult,
    LLMFailedRequest,
    LLMRequest,
    LLMResponseList,
)
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.constants.inference.openai import (
    BATCH_WAIT_AFTER_RATE_LIMIT_ERROR,
)
from math_rag.infrastructure.enums.inference.openai import BatchErrorCode
from math_rag.infrastructure.inference.partials import PartialBatchLLM
from math_rag.infrastructure.mappings.inference.openai import (
    LLMErrorMapping,
    LLMRequestMapping,
    LLMResponseListMapping,
)
from math_rag.infrastructure.utils import TokenCounterUtil
from math_rag.infrastructure.validators.inference.openai import OpenAIValidator


logger = getLogger(__name__)


class OpenAIBatchLLM(PartialBatchLLM):
    def __init__(self, client: AsyncOpenAI):
        self.client = client
        self.batch_request_id_to_input_file_id: dict[UUID, str] = {}

    async def batch_generate_init(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
        *,
        max_tokens_per_day: float | None,
    ) -> str:
        # validate
        if max_tokens_per_day is None:
            raise ValueError(f'{self.__class__.__name__} requires max_tokens_per_day')

        model = batch_request.requests[0].params.model
        OpenAIValidator.validate_model_name(model)

        # check token limit
        total_tokens = sum(
            TokenCounterUtil.count(request, model_name=model)
            for request in batch_request.requests
        )

        if total_tokens > max_tokens_per_day:
            raise ValueError(
                f'Batch request {batch_request.id} exceeds token limit '
                f'{total_tokens}/{max_tokens_per_day}'
            )

        # check if the file already exists
        input_file = None
        input_file_ids = self.batch_request_id_to_input_file_id.values()

        if input_file_ids:
            async for file in self.client.files.list():
                if file.id in input_file_ids:
                    input_file = file
                    break

        if not input_file:
            # map requests
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

            # create in-memory input file
            lines = [
                json.dumps(request_dict, separators=(',', ':'))
                for request_dict in request_dicts
            ]
            jsonl_str = '\n'.join(lines)
            jsonl_bytes = jsonl_str.encode('utf-8')

            # create openai input file
            input_file = await self.client.files.create(
                file=jsonl_bytes, purpose='batch'
            )
            self.batch_request_id_to_input_file_id[batch_request.id] = input_file.id

        try:
            batch = await self.client.batches.create(
                input_file_id=input_file.id,
                endpoint=url,
                completion_window='24h',
                metadata=None,
            )

        except BadRequestError as e:
            if 'token_limit_exceeded' in str(e):
                sleep(BATCH_WAIT_AFTER_RATE_LIMIT_ERROR)

                return await self.batch_generate_init(
                    batch_request, max_tokens_per_day=max_tokens_per_day
                )

            raise

        # check errors
        batch_error_codes = [code for code in BatchErrorCode]

        if batch.errors:
            logger.warning(f'Cancelling batch {batch.id} due to an error')
            await self.client.batches.cancel(batch.id)

            if batch.errors.data:
                for batch_error in batch.errors.data:
                    batch_error_code_label = (
                        'Unknown'
                        if batch_error.code not in batch_error_codes
                        else 'Known'
                    )

                    logger.error(
                        f'{batch_error_code_label} batch error - '
                        f'code: {batch_error.code}, '
                        f'line: {batch_error.line}, '
                        f'message: {batch_error.message}, '
                        f'param: {batch_error.param}'
                    )

                raise ValueError(
                    f'Batch {batch.id} has {len(batch.errors.data)} error(s)'
                )

        logger.info(
            f'Batch {batch.id} created for '
            f'batch request {batch_request.id} '
            f'with status {batch.status}'
        )

        # cleanup
        self.batch_request_id_to_input_file_id.pop(batch_request.id)

        return batch.id

    async def batch_generate_result(
        self,
        batch_id: str,
        batch_request_id: UUID,
        response_type: type[LLMResponseType],
    ) -> LLMBatchResult[LLMResponseType] | None:
        batch = await self.client.batches.retrieve(batch_id)

        logger.info(
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
            batch_request_id=batch_request_id,
            response_lists=response_lists,
            failed_requests=failed_requests,
        )

        await self.client.files.delete(batch.input_file_id)
        await self.client.files.delete(batch.output_file_id)

        return batch_result
