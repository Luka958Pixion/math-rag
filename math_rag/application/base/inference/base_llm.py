from .base_basic_llm import BaseBasicLLM
from .base_batch_llm import BaseBatchLLM
from .base_concurrent_llm import BaseConcurrentLLM


class BaseLLM(BaseBasicLLM, BaseBatchLLM, BaseConcurrentLLM):
    pass
