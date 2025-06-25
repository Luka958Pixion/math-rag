from math_rag.core.models.fine_tune_settings import SFTSettings
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents.fine_tune_settings import SFTSettingsDocument


class SFTSettingsMapping(BaseMapping[SFTSettings, SFTSettingsDocument]):
    @staticmethod
    def to_source(target: SFTSettingsDocument) -> SFTSettings:
        return SFTSettings.model_validate(target.model_dump())

    @staticmethod
    def to_target(source: SFTSettings) -> SFTSettingsDocument:
        return SFTSettingsDocument.model_validate(source.model_dump())
