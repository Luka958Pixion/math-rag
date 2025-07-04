from tiktoken import encoding_for_model, get_encoding

from math_rag.application.models.inference import MMRequest


class MMTokenCounterUtil:
    @staticmethod
    def count(
        request: MMRequest,
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

        return len(encoding.encode(request.text))
