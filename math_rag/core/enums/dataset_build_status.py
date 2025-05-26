from enum import Enum


class DatasetBuildStatus(str, Enum):
    PENDING = 'pending'
    RUNNING = 'running'
    FINISHED = 'finished'
    FAILED = 'failed'
