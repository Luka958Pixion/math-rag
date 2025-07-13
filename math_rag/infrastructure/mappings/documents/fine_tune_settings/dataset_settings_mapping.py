from math_rag.core.models.fine_tune_settings import DatasetSettings
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents.fine_tune_settings import DatasetSettingsDocument


class DatasetSettingsMapping(BaseMapping[DatasetSettings, DatasetSettingsDocument]):
    @staticmethod
    def to_source(target: DatasetSettingsDocument) -> DatasetSettings:
        return DatasetSettings(dataset_name=target.dataset_name, config_name=target.config_name)

    @staticmethod
    def to_target(source: DatasetSettings) -> DatasetSettingsDocument:
        return DatasetSettingsDocument(
            dataset_name=source.dataset_name, config_name=source.config_name
        )
