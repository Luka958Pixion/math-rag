from pydantic import BaseModel

from .optuna_lora_settings import OptunaTrialSettings
from .optuna_lora_start_settings import OptunaTrialStartSettings
from .optuna_study_settings import OptunaStudySettings


class OptunaSettings(BaseModel):
    study_settings: OptunaStudySettings
    trial_start_settings: OptunaTrialStartSettings
    trial_settings: OptunaTrialSettings
    n_trials: int
    metric_name: str
