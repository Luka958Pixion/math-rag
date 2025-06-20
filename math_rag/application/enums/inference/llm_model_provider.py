from enum import Enum


class LLMModelProvider(str, Enum):
    OPEN_AI = 'openai'
    META = 'meta'
