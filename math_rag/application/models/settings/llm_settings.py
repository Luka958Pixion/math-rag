from pydantic import BaseModel

from .basic_llm_settings import BasicLLMSettings
from .batch_llm_settings import BatchLLMSettings
from .concurrent_llm_settings import ConcurrentLLMSettings


class LLMSettings(BaseModel):
    basic: BasicLLMSettings | None = None
    batch: BatchLLMSettings | None = None
    concurrent: ConcurrentLLMSettings | None = None
