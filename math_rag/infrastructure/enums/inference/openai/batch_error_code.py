from enum import Enum


class BatchErrorCode(str, Enum):
    INVALID_JSON_LINE = 'invalid_json_line'
    TOKEN_LIMIT_EXCEEDED = 'token_limit_exceeded'
