from math_rag.infrastructure.base import BaseDocument


class OptunaTrialStartSettingsDocument(BaseDocument):
    r: int
    lora_alpha: int
    lora_dropout: float
