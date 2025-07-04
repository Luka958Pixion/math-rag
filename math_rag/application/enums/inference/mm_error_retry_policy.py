from enum import Enum


class MMErrorRetryPolicy(str, Enum):
    RETRY = 'retry'
    NO_RETRY = 'no_retry'
