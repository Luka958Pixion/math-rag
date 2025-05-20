from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    ContentFilterFinishReasonError,
    InternalServerError,
    LengthFinishReasonError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    UnprocessableEntityError,
)


OPENAI_ERRORS_TO_RETRY = (
    APIConnectionError,  # NOTE: occured besides having proper connection settings
    APITimeoutError,
    InternalServerError,
    RateLimitError,
    UnprocessableEntityError,
)
OPENAI_ERRORS_TO_NOT_RETRY = (LengthFinishReasonError, ContentFilterFinishReasonError)
OPENAI_ERRORS_TO_RETRY_NO_RATE_LIMIT = (
    APITimeoutError,
    InternalServerError,
    UnprocessableEntityError,
)
OPENAI_ERRORS_TO_RAISE = (
    AuthenticationError,
    BadRequestError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
)
