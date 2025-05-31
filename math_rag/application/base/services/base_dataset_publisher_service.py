from abc import ABC, abstractmethod

from math_rag.application.models.datasets import (
    DatasetMetadataFile,
    DatasetSplitSettings,
)
from math_rag.core.base import BaseDataset


class BaseDatasetPublisherService(ABC):
    @abstractmethod
    def publish(
        self,
        dataset: BaseDataset,
        dataset_split_settings: DatasetSplitSettings,
        dataset_metadata_file: DatasetMetadataFile | None,
    ):
        pass
