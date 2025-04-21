from .base_basic_em import BaseBasicEM
from .base_batch_em import BaseBatchEM
from .base_concurrent_em import BaseConcurrentEM


class BaseUnifiedEM(BaseBasicEM, BaseBatchEM, BaseConcurrentEM):
    pass
