from enum import Enum


class MathExpressionDatasetBuildStatus(str, Enum):
    PENDING = 'pending'
    RUNNING = 'running'
    FINISHED = 'finished'
    FAILED = 'failed'
