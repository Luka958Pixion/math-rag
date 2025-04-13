from tiktoken import get_encoding

from math_rag.application.models.inference import LLMRequest
from math_rag.application.types.inference import LLMResponseType
from math_rag.infrastructure.constants.inference.openai import (
    ENCODING_NAME,
    MAX_COMPLETION_TOKENS,
)


class TokenCounterUtil:
    @staticmethod
    def count(request: LLMRequest[LLMResponseType], encoding_name: str | None = None):
        encoding_name = encoding_name or ENCODING_NAME
        encoding = get_encoding(encoding_name)

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
