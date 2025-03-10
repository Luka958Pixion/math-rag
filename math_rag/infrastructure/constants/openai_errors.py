from openai import (
    APIConnectionError,
    APITimeoutError,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    InternalServerError,
    NotFoundError,
    PermissionDeniedError,
    RateLimitError,
    UnprocessableEntityError,
)


OPENAI_ERRORS_TO_RETRY = (
    APITimeoutError,
    InternalServerError,
    RateLimitError,
    UnprocessableEntityError,
)
OPENAI_ERRORS_TO_RETRY_NO_RATE_LIMIT = (
    APITimeoutError,
    InternalServerError,
    UnprocessableEntityError,
)
OPENAI_ERRORS_TO_RAISE = (
    APIConnectionError,
    AuthenticationError,
    BadRequestError,
    ConflictError,
    NotFoundError,
    PermissionDeniedError,
)
