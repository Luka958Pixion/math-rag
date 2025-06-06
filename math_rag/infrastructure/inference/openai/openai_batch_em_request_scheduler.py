import json

from asyncio import sleep
from collections.abc import AsyncGenerator
from datetime import datetime, timedelta

from math_rag.application.base.inference import (
    BaseBatchEMRequestScheduler,
    BaseBatchManagedEM,
)
from math_rag.application.models.inference import (
    EMBatchRequest,
    EMBatchRequestSchedule,
    EMBatchRequestScheduleEntry,
    EMBatchResult,
)
from math_rag.infrastructure.mappings.inference.openai import EMRequestMapping
from math_rag.infrastructure.utils import EMTokenCounterUtil
from math_rag.infrastructure.validators.inference.openai import OpenAIModelNameValidator


class OpenAIBatchEMRequestScheduler(BaseBatchEMRequestScheduler):
    def __init__(self, em: BaseBatchManagedEM):
        self.em = em

    def schedule(
        self,
        batch_request: EMBatchRequest,
        *,
        max_tokens_per_day: float,
        max_input_file_size: int,
    ) -> EMBatchRequestSchedule:
        if not batch_request.requests:
            raise ValueError(f'Batch request {batch_request.id} is empty')

        model = batch_request.requests[0].params.model
        OpenAIModelNameValidator.validate(model)

        current_tokens = 0
        current_input_file_size = 0
        current_batch_request = EMBatchRequest(requests=[])
        schedule = EMBatchRequestSchedule(entries=[])
        schedule_timestamp = datetime.now()

        for request in batch_request.requests:
            # estimate tokens
            tokens = EMTokenCounterUtil.count(request, model_name=model)

            # estimate input file size
            request_dict = {
                'custom_id': str(request.id),
                'method': 'POST',
                'url': '/v1/embeddings',
                'body': EMRequestMapping.to_target(request, use_parsed=True),
            }
            jsonl_str = json.dumps(request_dict, separators=(',', ':'))
            jsonl_bytes = jsonl_str.encode('utf-8')
            input_file_size = len(jsonl_bytes)

            # check if adding this request would exceed limits
            exceeds_tokens = (current_tokens + tokens) > max_tokens_per_day
            exceeds_size = (current_input_file_size + input_file_size) > max_input_file_size

            if current_batch_request and (exceeds_tokens or exceeds_size):
                # append new schedule entry
                schedule_entry = EMBatchRequestScheduleEntry(
                    batch_request=current_batch_request, timestamp=schedule_timestamp
                )
                schedule.entries.append(schedule_entry)

                # prepare next batch and reset counters
                schedule_timestamp += timedelta(days=1)
                current_batch_request = EMBatchRequest(requests=[])
                current_tokens = 0
                current_input_file_size = 0

            # add the request to the batch
            current_batch_request.requests.append(request)
            current_tokens += tokens
            current_input_file_size += input_file_size

        if current_batch_request.requests:
            # append final schedule entry is any
            schedule_entry = EMBatchRequestScheduleEntry(
                batch_request=current_batch_request, timestamp=schedule_timestamp
            )
            schedule.entries.append(schedule_entry)

        return schedule

    async def execute(
        self,
        schedule: EMBatchRequestSchedule,
    ) -> AsyncGenerator[EMBatchResult, None]:
        for entry in schedule.entries:
            current_timestamp = datetime.now()

            if current_timestamp < entry.timestamp:
                await sleep(entry.timestamp - current_timestamp)

            yield await self.em.batch_embed(entry.batch_request)
