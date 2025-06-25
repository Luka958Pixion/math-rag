from pydantic import BaseModel

from .optuna_study_settings import OptunaStudySettings
from .optuna_trial_settings import OptunaTrialSettings
from .optuna_trial_start_settings import OptunaTrialStartSettings


class OptunaSettings(BaseModel):
    n_trials: int
    metric_name: str
    study_settings: OptunaStudySettings
    trial_start_settings: OptunaTrialStartSettings
    trial_settings: OptunaTrialSettings
