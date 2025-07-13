from math_rag.core.models.fine_tune_settings import ModelSettings
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents.fine_tune_settings import ModelSettingsDocument


class ModelSettingsMapping(BaseMapping[ModelSettings, ModelSettingsDocument]):
    @staticmethod
    def to_source(target: ModelSettingsDocument) -> ModelSettings:
        return ModelSettings(
            model_name=target.model_name,
            target_modules=target.target_modules,
            max_tokens=target.max_tokens,
        )

    @staticmethod
    def to_target(source: ModelSettings) -> ModelSettingsDocument:
        return ModelSettingsDocument(
            model_name=source.model_name,
            target_modules=source.target_modules,
            max_tokens=source.max_tokens,
        )
