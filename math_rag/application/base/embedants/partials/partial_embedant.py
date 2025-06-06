from math_rag.application.base.inference import BaseBatchEMRequestManagedScheduler, BaseManagedEM
from math_rag.application.types.embedants import EmbedantInputType, EmbedantOutputType

from .partial_basic_embedant import PartialBasicEmbedant
from .partial_batch_embedant import PartialBatchEmbedant
from .partial_concurrent_embedant import PartialConcurrentEmbedant


class PartialEmbedant(
    PartialBasicEmbedant[EmbedantInputType, EmbedantOutputType],
    PartialBatchEmbedant[EmbedantInputType, EmbedantOutputType],
    PartialConcurrentEmbedant[EmbedantInputType, EmbedantOutputType],
):
    def __init__(self, em: BaseManagedEM, scheduler: BaseBatchEMRequestManagedScheduler | None):
        PartialBasicEmbedant.__init__(self, em)
        PartialBatchEmbedant.__init__(self, em, scheduler)
        PartialConcurrentEmbedant.__init__(self, em)
