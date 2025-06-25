from math_rag.infrastructure.base import BaseDocument


class DatasetSettingsDocument(BaseDocument):
    dataset_name: str
    config_name: str
