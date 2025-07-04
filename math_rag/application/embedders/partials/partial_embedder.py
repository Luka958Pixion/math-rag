from math_rag.application.base.inference import BaseBatchEMRequestManagedScheduler, BaseManagedEM
from math_rag.application.types.embedders import EmbedderInputType, EmbedderOutputType

from .partial_basic_embedder import PartialBasicEmbedder
from .partial_batch_embedder import PartialBatchEmbedder
from .partial_concurrent_embedder import PartialConcurrentEmbedder


class PartialEmbedder(
    PartialBasicEmbedder[EmbedderInputType, EmbedderOutputType],
    PartialBatchEmbedder[EmbedderInputType, EmbedderOutputType],
    PartialConcurrentEmbedder[EmbedderInputType, EmbedderOutputType],
):
    def __init__(self, em: BaseManagedEM, scheduler: BaseBatchEMRequestManagedScheduler | None):
        PartialBasicEmbedder.__init__(self, em)
        PartialBatchEmbedder.__init__(self, em, scheduler)
        PartialConcurrentEmbedder.__init__(self, em)
