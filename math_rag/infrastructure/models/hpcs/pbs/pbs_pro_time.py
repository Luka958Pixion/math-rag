from datetime import datetime, timedelta

from pydantic import BaseModel, Field, field_validator


FORMAT = '%a %b %d %H:%M:%S %Y'


class PBSProTime(BaseModel):
    created: datetime = Field(alias='ctime')
    queued: datetime = Field(alias='qtime')
    modified: datetime = Field(alias='mtime')
    started: datetime = Field(alias='stime')
    eligible: datetime = Field(alias='etime')
    eligible_delta: timedelta = Field(alias='eligible_time')

    @field_validator(
        'created', 'queued', 'modified', 'started', 'eligible', mode='before'
    )
    def parse_datetime(cls, value: str) -> datetime:
        return datetime.strptime(value, FORMAT)
