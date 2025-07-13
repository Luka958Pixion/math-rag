from math_rag.core.models.fine_tune_settings import FineTuneSettings
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents.fine_tune_settings import FineTuneSettingsDocument


class FineTuneSettingsMapping(BaseMapping[FineTuneSettings, FineTuneSettingsDocument]):
    @staticmethod
    def to_source(target: FineTuneSettingsDocument) -> FineTuneSettings:
        return FineTuneSettings(
            dataset_settings=target.dataset_settings,
            model_settings=target.model_settings,
            optimizer_settings=target.optimizer_settings,
            optuna_settings=target.optuna_settings,
            sft_settings=target.sft_settings,
        )

    @staticmethod
    def to_target(source: FineTuneSettings) -> FineTuneSettingsDocument:
        return FineTuneSettingsDocument(
            dataset_settings=source.dataset_settings,
            model_settings=source.model_settings,
            optimizer_settings=source.optimizer_settings,
            optuna_settings=source.optuna_settings,
            sft_settings=source.sft_settings,
        )
