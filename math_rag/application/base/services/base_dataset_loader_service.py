from abc import ABC, abstractmethod
from uuid import UUID

from math_rag.application.models.datasets import DatasetMetadataFile
from math_rag.core.types import SampleType


class BaseDatasetLoaderService(ABC):
    @abstractmethod
    def load(
        self,
        dataset_id: UUID,
        dataset_name: str,
        dataset_metadata_file_name: str | None,
        sample_type: type[SampleType],
        *,
        max_retries: int,
    ) -> tuple[dict[str, list[SampleType]], DatasetMetadataFile | None]:
        pass
