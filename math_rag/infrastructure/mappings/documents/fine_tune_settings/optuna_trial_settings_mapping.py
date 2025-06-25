from math_rag.core.models.fine_tune_settings import OptunaTrialSettings
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents.fine_tune_settings import OptunaTrialSettingsDocument


class OptunaTrialSettingsMapping(BaseMapping[OptunaTrialSettings, OptunaTrialSettingsDocument]):
    @staticmethod
    def to_source(target: OptunaTrialSettingsDocument) -> OptunaTrialSettings:
        return OptunaTrialSettings.model_validate(target.model_dump())

    @staticmethod
    def to_target(source: OptunaTrialSettings) -> OptunaTrialSettingsDocument:
        return OptunaTrialSettingsDocument.model_validate(source.model_dump())
