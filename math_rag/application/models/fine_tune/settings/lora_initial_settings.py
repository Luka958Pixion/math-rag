from pydantic import BaseModel


class LoRAInitialSettings(BaseModel):
    r: int
    lora_alpha: int
    lora_dropout: float
