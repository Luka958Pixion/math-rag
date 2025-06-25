from math_rag.infrastructure.base import BaseDocument


class SFTSettingsDocument(BaseDocument):
    learning_rate: float
    per_device_train_batch_size: int
    gradient_accumulation_steps: int
    num_train_epochs: int
    weight_decay: float
    fp16: bool
