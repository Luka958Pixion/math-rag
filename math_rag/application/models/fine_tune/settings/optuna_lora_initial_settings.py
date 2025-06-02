from pydantic import BaseModel


class OptunaLoRAInitialSettings(BaseModel):
    r: int
    lora_alpha: int
    lora_dropout: float
