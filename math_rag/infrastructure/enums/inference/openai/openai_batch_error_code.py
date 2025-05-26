from enum import Enum


class OpenAIBatchErrorCode(str, Enum):
    """
    OpenAI batch error codes

    Reference:
        https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/batch?tabs=global-batch%2Cstandard-input%2Cpython-secure&pivots=ai-foundry-portal#error-codes
    """

    INVALID_JSON_LINE = 'invalid_json_line'
    TOO_MANY_TASKS = 'too_many_tasks'
    URL_MISMATCH = 'url_mismatch'
    MODEL_NOT_FOUND = 'model_not_found'
    DUPLICATE_CUSTOM_ID = 'duplicate_custom_id'
    EMPTY_BATCH = 'empty_batch'
    MODEL_MISMATCH = 'model_mismatch'
    INVALID_REQUEST = 'invalid_request'
