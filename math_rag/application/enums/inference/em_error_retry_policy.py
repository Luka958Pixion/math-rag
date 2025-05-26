from enum import Enum


class EMErrorRetryPolicy(str, Enum):
    RETRY = 'retry'
    NO_RETRY = 'no_retry'
