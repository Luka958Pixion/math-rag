from uuid import UUID

from math_rag.application.base.services import BaseDatasetLoaderService
from math_rag.core.types import SampleType


class LabelStudioPublisherService:
    def __init__(self, dataset_loader_service: BaseDatasetLoaderService):
        self.dataset_loader_service = dataset_loader_service

    async def publish(
        self,
        dataset_id: UUID,
        dataset_name: str,
        split_name: str,
        sample_type: type[SampleType],
    ):
        split_name_to_samples, _ = self.dataset_loader_service.load(
            dataset_id=dataset_id,
            dataset_name=dataset_name,
            dataset_metadata_file_name=None,
            sample_type=sample_type,
            max_retries=3,
        )
        samples = split_name_to_samples[split_name]

        # TODO get labels -> pass as arg
