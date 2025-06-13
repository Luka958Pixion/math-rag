from abc import ABC, abstractmethod
from uuid import UUID

from math_rag.application.models.datasets import DatasetMetadataFile
from math_rag.core.models import DatasetSplit
from math_rag.core.types import SampleType


class BaseDatasetPublisherService(ABC):
    @abstractmethod
    def publish(
        self,
        dataset_id: UUID,
        dataset_name: str,
        samples: list[SampleType],
        sample_type: type[SampleType],
        fields: list[str],
        dataset_splits: list[DatasetSplit],
        dataset_metadata_file: DatasetMetadataFile | None,
    ):
        pass

    @abstractmethod
    def unpublish(self, dataset_name: str):
        pass
