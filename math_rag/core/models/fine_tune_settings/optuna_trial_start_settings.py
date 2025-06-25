from pydantic import BaseModel


class OptunaTrialStartSettings(BaseModel):
    r: int
    lora_alpha: int
    lora_dropout: float
