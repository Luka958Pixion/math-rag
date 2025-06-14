from enum import Enum


class LLMProvider(str, Enum):
    OPEN_AI = 'openai'
    META = 'meta'
