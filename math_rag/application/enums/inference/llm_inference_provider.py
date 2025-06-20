from enum import Enum


class LLMInferenceProvider(str, Enum):
    OPEN_AI = 'openai'
    HUGGING_FACE = 'huggingface'
