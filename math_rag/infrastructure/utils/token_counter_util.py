from typing import overload

from tiktoken import encoding_for_model, get_encoding

from math_rag.application.models.inference import EMRequest, LLMRequest
from math_rag.application.types.inference import LLMResponseType


class TokenCounterUtil:
    @overload
    @staticmethod
    def count(
        request: EMRequest,
        *,
        encoding_name: str | None = None,
        model_name: str | None = None,
    ) -> int:
        pass

    @overload
    @staticmethod
    def count(
        request: LLMRequest[LLMResponseType],
        *,
        encoding_name: str | None = None,
        model_name: str | None = None,
    ) -> int:
        pass

    @staticmethod
    def count(
        request: EMRequest | LLMRequest[LLMResponseType],
        *,
        encoding_name: str | None = None,
        model_name: str | None = None,
    ) -> int:
        if encoding_name:
            encoding = get_encoding(encoding_name)

        elif model_name:
            encoding = encoding_for_model(model_name)

        else:
            raise ValueError('Missing encoding_name or model_name')

        if isinstance(request, EMRequest):
            return len(encoding.encode(request.text))

        prompt_tokens = sum(
            len(encoding.encode(message.content))
            for message in request.conversation.messages
        )
        max_completion_tokens = request.params.max_completion_tokens or 0
        completion_tokens = request.params.n * max_completion_tokens
        total_tokens = prompt_tokens + completion_tokens

        return total_tokens
