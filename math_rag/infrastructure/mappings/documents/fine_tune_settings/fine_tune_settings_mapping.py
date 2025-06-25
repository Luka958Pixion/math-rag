from math_rag.core.models.fine_tune_settings import FineTuneSettings
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents.fine_tune_settings import FineTuneSettingsDocument


class FineTuneSettingsMapping(BaseMapping[FineTuneSettings, FineTuneSettingsDocument]):
    @staticmethod
    def to_source(target: FineTuneSettingsDocument) -> FineTuneSettings:
        return FineTuneSettings.model_validate(target.model_dump())

    @staticmethod
    def to_target(source: FineTuneSettings) -> FineTuneSettingsDocument:
        return FineTuneSettingsDocument.model_validate(source.model_dump())
