from enum import Enum


class EMModelProvider(str, Enum):
    OPEN_AI = 'openai'

    @classmethod
    def from_str(cls, value: str) -> 'EMModelProvider':
        try:
            return cls[value.upper()]

        except KeyError:
            raise ValueError(f'EM model provider {value} not found in {cls.__name__}')
