from math_rag.core.models.fine_tune_settings import OptimizerSettings
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents.fine_tune_settings import OptimizerSettingsDocument


class OptimizerSettingsMapping(BaseMapping[OptimizerSettings, OptimizerSettingsDocument]):
    @staticmethod
    def to_source(target: OptimizerSettingsDocument) -> OptimizerSettings:
        return OptimizerSettings.model_validate(target.model_dump())

    @staticmethod
    def to_target(source: OptimizerSettings) -> OptimizerSettingsDocument:
        return OptimizerSettingsDocument.model_validate(source.model_dump())
