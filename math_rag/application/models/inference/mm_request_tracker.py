from pydantic import BaseModel, Field

from .mm_error import MMError
from .mm_request import MMRequest


class MMRequestTracker(BaseModel):
    request: MMRequest
    errors: list[MMError] = Field(default_factory=list)
    token_consumption: int
    retries_left: int
