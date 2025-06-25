from math_rag.core.models.fine_tune_settings import OptunaTrialStartSettings
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents.fine_tune_settings import (
    OptunaTrialStartSettingsDocument,
)


class OptunaTrialStartSettingsMapping(
    BaseMapping[OptunaTrialStartSettings, OptunaTrialStartSettingsDocument]
):
    @staticmethod
    def to_source(target: OptunaTrialStartSettingsDocument) -> OptunaTrialStartSettings:
        return OptunaTrialStartSettings.model_validate(target.model_dump())

    @staticmethod
    def to_target(source: OptunaTrialStartSettings) -> OptunaTrialStartSettingsDocument:
        return OptunaTrialStartSettingsDocument.model_validate(source.model_dump())
