from enum import Enum


class EMInferenceProvider(str, Enum):
    OPEN_AI = 'openai'
    HUGGING_FACE = 'huggingface'
