from math_rag.core.models.fine_tune_settings import OptunaStudySettings
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents.fine_tune_settings import OptunaStudySettingsDocument


class OptunaStudySettingsMapping(BaseMapping[OptunaStudySettings, OptunaStudySettingsDocument]):
    @staticmethod
    def to_source(target: OptunaStudySettingsDocument) -> OptunaStudySettings:
        return OptunaStudySettings.model_validate(target.model_dump())

    @staticmethod
    def to_target(source: OptunaStudySettings) -> OptunaStudySettingsDocument:
        return OptunaStudySettingsDocument.model_validate(source.model_dump())
