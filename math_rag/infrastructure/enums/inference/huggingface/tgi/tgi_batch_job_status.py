from enum import Enum


class TGIBatchJobStatus(str, Enum):
    READY = 'ready'
    PENDING = 'pending'
    RUNNING = 'running'
    FINISHED = 'finished'
    FAILED = 'failed'
