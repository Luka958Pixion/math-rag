from abc import ABC, abstractmethod

from math_rag.application.base.datasets import BaseDataset, BaseSample
from math_rag.application.models.datasets import (
    DatasetMetadataFile,
    DatasetSplitSettings,
)


class BaseDatasetPublisherService(ABC):
    @abstractmethod
    def publish(
        self,
        dataset: BaseDataset,
        sample_type: type[BaseSample],
        dataset_split_settings: DatasetSplitSettings,
        dataset_metadata_file: DatasetMetadataFile | None,
    ):
        pass
