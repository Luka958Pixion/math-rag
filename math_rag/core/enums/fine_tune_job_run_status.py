from enum import Enum


class FineTuneJobRunStatus(str, Enum):
    PENDING = 'pending'
    RUNNING = 'running'
    FINISHED = 'finished'
    FAILED = 'failed'
