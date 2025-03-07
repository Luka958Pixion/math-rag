from typing import Generic

from pydantic import BaseModel

from math_rag.application.types import LLMResponseType

from .llm_request_batch import LLMRequestBatch
from .llm_response import LLMResponse


class LLMResponseBatch(BaseModel, Generic[LLMResponseType]):
    request_batch: LLMRequestBatch[LLMResponseType]
    responses: list[
        LLMResponse[LLMResponseType]
    ]  # TODO: responses for multiple choices, which request did you asnwer to
    # TODO how will assistant use batch api
