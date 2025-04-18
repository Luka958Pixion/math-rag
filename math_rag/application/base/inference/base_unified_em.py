from .base_batch_em import BaseBatchEM
from .base_concurrent_em import BaseConcurrentEM
from .base_em import BaseEM


class BaseUnifiedEM(BaseEM, BaseBatchEM, BaseConcurrentEM):
    pass
