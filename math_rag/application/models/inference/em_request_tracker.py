from pydantic import BaseModel, Field

from .em_error import EMError
from .em_request import EMRequest


class EMRequestTracker(BaseModel):
    request: EMRequest
    errors: list[EMError] = Field(default_factory=list)
    token_consumption: int
    retries_left: int
