from .base_basic_managed_mm import BaseBasicManagedMM
from .base_concurrent_managed_mm import BaseConcurrentManagedMM


class BaseManagedMM(BaseBasicManagedMM, BaseConcurrentManagedMM):
    pass
