from typing import overload

from tiktoken import get_encoding

from math_rag.application.models.inference import EMRequest, LLMRequest
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.constants.inference.openai import (
    ENCODING_NAME,
    MAX_COMPLETION_TOKENS,
)


class TokenCounterUtil:
    @overload
    @staticmethod
    def count(request: EMRequest, encoding_name: str | None = None) -> int:
        pass

    @overload
    @staticmethod
    def count(
        request: LLMRequest[LLMResponseType], encoding_name: str | None = None
    ) -> int:
        pass

    @staticmethod
    def count(
        request: EMRequest | LLMRequest[LLMResponseType],
        encoding_name: str | None = None,
    ) -> int:
        encoding_name = encoding_name or ENCODING_NAME
        encoding = get_encoding(encoding_name)

        if isinstance(request, EMRequest):
            return len(encoding.encode(request.text))

        prompt_tokens = sum(
            len(encoding.encode(message.content))
            for message in request.conversation.messages
        )
        max_completion_tokens = (
            request.params.max_completion_tokens or MAX_COMPLETION_TOKENS
        )
        completion_tokens = request.params.n * max_completion_tokens
        total_tokens = prompt_tokens + completion_tokens

        return total_tokens
