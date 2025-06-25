from pydantic import BaseModel


class OptimizerSettings(BaseModel):
    lr: float
    weight_decay: float
