from pydantic import BaseModel

from .optuna_lora_initial_settings import OptunaLoRAInitialSettings
from .optuna_lora_settings import OptunaLoRASettings


class OptunaSettings(BaseModel):
    study_name: str
    metric_name: str
    direction: str
    n_trials: int
    lora_initial_settings: OptunaLoRAInitialSettings
    lora_settings: OptunaLoRASettings
