from math_rag.infrastructure.base import BaseDocument


class OptimizerSettingsDocument(BaseDocument):
    lr: float
    weight_decay: float
