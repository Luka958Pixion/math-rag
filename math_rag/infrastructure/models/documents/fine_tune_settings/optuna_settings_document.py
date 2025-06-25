from math_rag.infrastructure.base import BaseDocument

from .optuna_study_settings_document import OptunaStudySettingsDocument
from .optuna_trial_settings_document import OptunaTrialSettingsDocument
from .optuna_trial_start_settings_document import OptunaTrialStartSettingsDocument


class OptunaSettingsDocument(BaseDocument):
    n_trials: int
    metric_name: str
    study_settings: OptunaStudySettingsDocument
    trial_start_settings: OptunaTrialStartSettingsDocument
    trial_settings: OptunaTrialSettingsDocument
