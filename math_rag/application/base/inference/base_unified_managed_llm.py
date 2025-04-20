from .base_batch_managed_llm import BaseBatchManagedLLM
from .base_concurrent_managed_llm import BaseConcurrentManagedLLM
from .base_managed_llm import BaseManagedLLM


class BaseUnifiedManagedLLM(
    BaseManagedLLM, BaseBatchManagedLLM, BaseConcurrentManagedLLM
):
    pass
