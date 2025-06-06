from uuid import UUID, uuid4

from pydantic import BaseModel, Field, model_validator

from .em_batch_request_schedule_entry import EMBatchRequestScheduleEntry


class EMBatchRequestSchedule(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    entries: list[EMBatchRequestScheduleEntry]

    @model_validator(mode='after')
    def check_sorted_entries(self):
        timestamps = [entry.timestamp for entry in self.entries]

        for previous, current in zip(timestamps, timestamps[1:]):
            if previous >= current:
                raise ValueError(
                    'Entries must be sorted in strictly ascending order by scheduled_timestamp'
                )

        return self
