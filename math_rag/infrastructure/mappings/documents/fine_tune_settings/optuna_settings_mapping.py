from math_rag.core.models.fine_tune_settings import OptunaSettings
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents.fine_tune_settings import OptunaSettingsDocument


class OptunaSettingsMapping(BaseMapping[OptunaSettings, OptunaSettingsDocument]):
    @staticmethod
    def to_source(target: OptunaSettingsDocument) -> OptunaSettings:
        return OptunaSettings.model_validate(target.model_dump())

    @staticmethod
    def to_target(source: OptunaSettings) -> OptunaSettingsDocument:
        return OptunaSettingsDocument.model_validate(source.model_dump())
