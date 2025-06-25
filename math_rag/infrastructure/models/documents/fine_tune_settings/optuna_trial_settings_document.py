from math_rag.infrastructure.base import BaseDocument

from .optuna_float_param_document import OptunaFloatParamDocument
from .optuna_int_param_document import OptunaIntParamDocument


class OptunaTrialSettingsDocument(BaseDocument):
    r: OptunaIntParamDocument
    lora_alpha: OptunaIntParamDocument
    lora_dropout: OptunaFloatParamDocument
