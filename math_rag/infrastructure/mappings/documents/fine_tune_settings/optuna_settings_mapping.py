from math_rag.core.models.fine_tune_settings import OptunaSettings
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents.fine_tune_settings import OptunaSettingsDocument


class OptunaSettingsMapping(BaseMapping[OptunaSettings, OptunaSettingsDocument]):
    @staticmethod
    def to_source(target: OptunaSettingsDocument) -> OptunaSettings:
        return OptunaSettings(
            n_trials=target.n_trials,
            metric_name=target.metric_name,
            study_settings=target.study_settings,
            trial_start_settings=target.trial_start_settings,
            trial_settings=target.trial_settings,
        )

    @staticmethod
    def to_target(source: OptunaSettings) -> OptunaSettingsDocument:
        return OptunaSettingsDocument(
            n_trials=source.n_trials,
            metric_name=source.metric_name,
            study_settings=source.study_settings,
            trial_start_settings=source.trial_start_settings,
            trial_settings=source.trial_settings,
        )
