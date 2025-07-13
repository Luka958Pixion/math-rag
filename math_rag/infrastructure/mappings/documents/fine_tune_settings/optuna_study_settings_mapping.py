from math_rag.core.models.fine_tune_settings import OptunaStudySettings
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents.fine_tune_settings import OptunaStudySettingsDocument


class OptunaStudySettingsMapping(BaseMapping[OptunaStudySettings, OptunaStudySettingsDocument]):
    @staticmethod
    def to_source(target: OptunaStudySettingsDocument) -> OptunaStudySettings:
        return OptunaStudySettings(
            storage=target.storage,
            study_name=target.study_name,
            direction=target.direction,
            load_if_exists=target.load_if_exists,
        )

    @staticmethod
    def to_target(source: OptunaStudySettings) -> OptunaStudySettingsDocument:
        return OptunaStudySettingsDocument(
            storage=source.storage,
            study_name=source.study_name,
            direction=source.direction,
            load_if_exists=source.load_if_exists,
        )
