from enum import Enum


class LLMModelProvider(str, Enum):
    OPEN_AI = 'openai'
    META = 'meta'

    @classmethod
    def from_str(cls, value: str) -> 'LLMModelProvider':
        try:
            return cls[value.upper()]

        except KeyError:
            raise ValueError(f'LLM model provider {value} not found in {cls.__name__}')
