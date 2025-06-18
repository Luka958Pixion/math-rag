from enum import Enum


class EMInferenceProvider(str, Enum):
    OPEN_AI = 'openai'
    HUGGING_FACE = 'huggingface'

    @classmethod
    def from_str(cls, value: str) -> 'EMInferenceProvider':
        try:
            return cls[value.upper()]

        except KeyError:
            raise ValueError(f'EM inference provider {value} not found in {cls.__name__}')
