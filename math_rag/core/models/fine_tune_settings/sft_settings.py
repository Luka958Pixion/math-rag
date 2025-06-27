from pydantic import BaseModel


class SFTSettings(BaseModel):
    learning_rate: float
    per_device_train_batch_size: int
    gradient_accumulation_steps: int
    num_train_epochs: int
    weight_decay: float
    bf16: bool
    fp16: bool
