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
        return OptunaTrialStartSettings(
            r=target.r,
            lora_alpha=target.lora_alpha,
            lora_dropout=target.lora_dropout,
        )

    @staticmethod
    def to_target(source: OptunaTrialStartSettings) -> OptunaTrialStartSettingsDocument:
        return OptunaTrialStartSettingsDocument(
            r=source.r,
            lora_alpha=source.lora_alpha,
            lora_dropout=source.lora_dropout,
        )
