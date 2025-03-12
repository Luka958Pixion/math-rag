from .base_batch_llm import BaseBatchLLM
from .base_concurrent_llm import BaseConcurrentLLM
from .base_llm import BaseLLM


class BaseUnifiedLLM(BaseLLM, BaseBatchLLM, BaseConcurrentLLM):
    pass
