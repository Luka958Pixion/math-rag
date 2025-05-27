from .base_basic_managed_llm import BaseBasicManagedLLM
from .base_batch_managed_llm import BaseBatchManagedLLM
from .base_concurrent_managed_llm import BaseConcurrentManagedLLM


class BaseManagedLLM(BaseBasicManagedLLM, BaseBatchManagedLLM, BaseConcurrentManagedLLM):
    pass
