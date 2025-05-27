from tiktoken import encoding_for_model, get_encoding

from math_rag.application.models.inference import LLMRequest
from math_rag.application.types.inference import LLMResponseType


class LLMTokenCounterUtil:
    @staticmethod
    def count(
        request: LLMRequest[LLMResponseType],
        *,
        encoding_name: str | None = None,
        model_name: str | None = None,
    ) -> int:
        if encoding_name:
            encoding = get_encoding(encoding_name)

        elif model_name:
            # TODO: remove the if branch after tiktoken update
            if model_name.startswith('gpt-4.1'):
                encoding = get_encoding('o200k_base')

            else:
                encoding = encoding_for_model(model_name)

        else:
            raise ValueError('Missing encoding_name or model_name')

        prompt_tokens = sum(
            len(encoding.encode(message.content)) for message in request.conversation.messages
        )
        max_completion_tokens = request.params.max_completion_tokens or 0
        completion_tokens = request.params.n * max_completion_tokens
        total_tokens = prompt_tokens + completion_tokens

        return total_tokens
