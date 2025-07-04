from enum import Enum


class MMModelProvider(str, Enum):
    OPEN_AI = 'openai'

    @classmethod
    def from_str(cls, value: str) -> 'MMModelProvider':
        try:
            return cls[value.upper()]

        except KeyError:
            raise ValueError(f'MM model provider {value} not found in {cls.__name__}')
