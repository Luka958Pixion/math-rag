from math_rag.core.models.fine_tune_settings import ModelSettings
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents.fine_tune_settings import ModelSettingsDocument


class ModelSettingsMapping(BaseMapping[ModelSettings, ModelSettingsDocument]):
    @staticmethod
    def to_source(target: ModelSettingsDocument) -> ModelSettings:
        return ModelSettings.model_validate(target.model_dump())

    @staticmethod
    def to_target(source: ModelSettings) -> ModelSettingsDocument:
        return ModelSettingsDocument.model_validate(source.model_dump())
