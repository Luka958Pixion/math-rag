from enum import Enum


class HelperJobStatus(str, Enum):
    WAITING = 'waiting'
    RUNNING = 'running'
    FINISHED = 'finished'
    UNFINISHED = 'unfinished'
