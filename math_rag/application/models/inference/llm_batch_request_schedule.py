from typing import Generic
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

from math_rag.application.types.inference import LLMResponseType

from .llm_batch_request_schedule_entry import LLMBatchRequestScheduleEntry


class LLMBatchRequestSchedule(BaseModel, Generic[LLMResponseType]):
    id: UUID = Field(default_factory=uuid4)
    entries: list[LLMBatchRequestScheduleEntry[LLMResponseType]]

    @model_validator(mode='after')
    def check_sorted_entries(self):
        timestamps = [entry.scheduled_timestamp for entry in self.entries]

        for previous, current in zip(timestamps, timestamps[1:]):
            if previous >= current:
                raise ValueError(
                    'Entries must be sorted in strictly ascending order by scheduled_timestamp'
                )

        return self
