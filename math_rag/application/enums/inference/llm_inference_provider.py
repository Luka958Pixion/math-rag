from enum import Enum


class LLMInferenceProvider(str, Enum):
    OPEN_AI = 'openai'
    HUGGING_FACE = 'huggingface'

    @classmethod
    def from_str(cls, value: str) -> 'LLMInferenceProvider':
        try:
            return cls[value.upper()]

        except KeyError:
            raise ValueError(f'LLM inference provider {value} not found in {cls.__name__}')
