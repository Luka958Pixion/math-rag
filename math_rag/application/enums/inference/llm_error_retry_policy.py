from enum import Enum


class LLMErrorRetryPolicy(str, Enum):
    RETRY = 'retry'
    NO_RETRY = 'no_retry'
