from abc import ABC, abstractmethod

from math_rag.application.models.datasets import (
    DatasetMetadataFile,
    DatasetSplitSettings,
)
from math_rag.core.types import DatasetType, SampleType


class BaseDatasetPublisherService(ABC):
    @abstractmethod
    def publish(
        self,
        dataset: DatasetType,
        samples: list[SampleType],
        sample_type: type[SampleType],
        dataset_split_settings: DatasetSplitSettings,
        dataset_metadata_file: DatasetMetadataFile | None,
    ):
        pass
