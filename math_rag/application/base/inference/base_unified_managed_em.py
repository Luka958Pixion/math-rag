from .base_batch_managed_em import BaseBatchManagedEM
from .base_concurrent_managed_em import BaseConcurrentManagedEM
from .base_managed_em import BaseManagedEM


class BaseUnifiedManagedEM(BaseManagedEM, BaseBatchManagedEM, BaseConcurrentManagedEM):
    pass
