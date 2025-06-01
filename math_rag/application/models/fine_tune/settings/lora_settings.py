from pydantic import BaseModel

from .float_range import FloatRange
from .int_range import IntRange


class LoRASettings(BaseModel):
    r_range: IntRange
    lora_alpha_range: IntRange
    lora_dropout_range: FloatRange
