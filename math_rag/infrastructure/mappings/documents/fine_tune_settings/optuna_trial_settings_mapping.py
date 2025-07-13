from math_rag.core.models.fine_tune_settings import OptunaTrialSettings
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents.fine_tune_settings import (
    OptunaTrialSettingsDocument,
)


class OptunaTrialSettingsMapping(BaseMapping[OptunaTrialSettings, OptunaTrialSettingsDocument]):
    @staticmethod
    def to_source(target: OptunaTrialSettingsDocument) -> OptunaTrialSettings:
        return OptunaTrialSettings(
            r=target.r,
            lora_alpha=target.lora_alpha,
            lora_dropout=target.lora_dropout,
        )

    @staticmethod
    def to_target(source: OptunaTrialSettings) -> OptunaTrialSettingsDocument:
        return OptunaTrialSettingsDocument(
            r=source.r,
            lora_alpha=source.lora_alpha,
            lora_dropout=source.lora_dropout,
        )
