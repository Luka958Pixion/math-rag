from enum import Enum


class MMInferenceProvider(str, Enum):
    OPEN_AI = 'openai'

    @classmethod
    def from_str(cls, value: str) -> 'MMInferenceProvider':
        try:
            return cls[value.upper()]

        except KeyError:
            raise ValueError(f'MM inference provider {value} not found in {cls.__name__}')
