from pydantic import BaseModel

from .optuna_float_param import OptunaFloatParam
from .optuna_int_param import OptunaIntParam


class OptunaLoRASettings(BaseModel):
    r: OptunaIntParam
    lora_alpha: OptunaIntParam
    lora_dropout: OptunaFloatParam
