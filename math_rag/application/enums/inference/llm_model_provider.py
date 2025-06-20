from enum import Enum


class LLMModelProvider(str, Enum):
    OPEN_AI = 'openai'
    META_LLAMA = 'meta-llama'
