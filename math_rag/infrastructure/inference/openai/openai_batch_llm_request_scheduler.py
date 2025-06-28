import json

from asyncio import sleep
from collections.abc import AsyncGenerator
from datetime import datetime, timedelta

from math_rag.application.base.inference import BaseBatchLLMRequestScheduler
from math_rag.application.models.inference import (
    LLMBatchRequest,
    LLMBatchRequestSchedule,
    LLMBatchRequestScheduleEntry,
    LLMBatchResult,
)
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.mappings.inference.openai import LLMRequestMapping
from math_rag.infrastructure.utils import LLMTokenCounterUtil
from math_rag.infrastructure.validators.inference.openai import OpenAIModelNameValidator

from .openai_batch_managed_llm import OpenAIBatchManagedLLM


class OpenAIBatchLLMRequestScheduler(BaseBatchLLMRequestScheduler):
    def __init__(self, llm: OpenAIBatchManagedLLM):
        self.llm = llm

    def schedule(
        self,
        batch_request: LLMBatchRequest[LLMResponseType],
        *,
        max_tokens_per_day: float,
        max_input_file_size: int,
    ) -> LLMBatchRequestSchedule[LLMResponseType]:
        if not batch_request.requests:
            raise ValueError(f'Batch request {batch_request.id} is empty')

        model = batch_request.requests[0].params.model
        OpenAIModelNameValidator.validate(model)

        current_tokens = 0
        current_input_file_size = 0
        current_batch_request = LLMBatchRequest[LLMResponseType](requests=[])
        schedule = LLMBatchRequestSchedule[LLMResponseType](entries=[])
        schedule_timestamp = datetime.now()

        for request in batch_request.requests:
            # estimate tokens
            tokens = LLMTokenCounterUtil.count(request, model_name=model)

            # estimate input file size
            request_dict = {
                'custom_id': str(request.id),
                'method': 'POST',
                'url': '/v1/chat/completions',
                'body': LLMRequestMapping[LLMResponseType].to_target(request, use_parsed=True),
            }
            jsonl_str = json.dumps(request_dict, separators=(',', ':'))
            jsonl_bytes = jsonl_str.encode('utf-8')
            input_file_size = len(jsonl_bytes)

            # check if adding this request would exceed limits
            exceeds_tokens = (current_tokens + tokens) > max_tokens_per_day
            exceeds_size = (current_input_file_size + input_file_size) > max_input_file_size

            if current_batch_request.requests and (exceeds_tokens or exceeds_size):
                # append new schedule entry
                schedule_entry = LLMBatchRequestScheduleEntry[LLMResponseType](
                    batch_request=current_batch_request, timestamp=schedule_timestamp
                )
                schedule.entries.append(schedule_entry)

                # prepare next batch and reset counters
                schedule_timestamp += timedelta(days=1)
                current_batch_request = LLMBatchRequest[LLMResponseType](requests=[])
                current_tokens = 0
                current_input_file_size = 0

            # add the request to the batch
            current_batch_request.requests.append(request)
            current_tokens += tokens
            current_input_file_size += input_file_size

        if current_batch_request.requests:
            # append final schedule entry is any
            schedule_entry = LLMBatchRequestScheduleEntry[LLMResponseType](
                batch_request=current_batch_request, timestamp=schedule_timestamp
            )
            schedule.entries.append(schedule_entry)

        return schedule

    async def execute(
        self,
        schedule: LLMBatchRequestSchedule[LLMResponseType],
        response_type: type[LLMResponseType],
    ) -> AsyncGenerator[LLMBatchResult[LLMResponseType], None]:
        for entry in schedule.entries:
            current_timestamp = datetime.now()
            delta = entry.timestamp - current_timestamp
            seconds = delta.total_seconds()

            if seconds > 0:
                await sleep(seconds)

            yield await self.llm.batch_generate(entry.batch_request, response_type)
