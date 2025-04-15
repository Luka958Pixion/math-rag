from enum import Enum


class BatchJobStatus(str, Enum):
    WAITING = 'waiting'
    RUNNING = 'running'
    FINISHED = 'finished'
