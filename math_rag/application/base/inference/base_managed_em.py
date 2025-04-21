from .base_basic_managed_em import BaseBasicManagedEM
from .base_batch_managed_em import BaseBatchManagedEM
from .base_concurrent_managed_em import BaseConcurrentManagedEM


class BaseManagedEM(BaseBasicManagedEM, BaseBatchManagedEM, BaseConcurrentManagedEM):
    pass
