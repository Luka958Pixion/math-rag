from math_rag.core.enums import DatasetBuildStage, DatasetBuildStatus
from math_rag.core.models import Dataset
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import DatasetDocument


class DatasetMapping(BaseMapping[Dataset, DatasetDocument]):
    @staticmethod
    def to_source(target: DatasetDocument) -> Dataset:
        return Dataset(
            id=target.id,
            timestamp=target.timestamp,
            build_stage=DatasetBuildStage(target.build_stage),
            build_status=DatasetBuildStatus(target.build_status),
            build_from_dataset_id=target.build_from_dataset_id,
            build_from_stage=DatasetBuildStage(target.build_from_stage)
            if target.build_from_stage
            else None,
        )

    @staticmethod
    def to_target(source: Dataset) -> DatasetDocument:
        return DatasetDocument(
            id=source.id,
            timestamp=source.timestamp,
            build_stage=source.build_stage.value,
            build_status=source.build_status.value,
            build_from_dataset_id=source.build_from_dataset_id,
            build_from_stage=source.build_from_stage.value if source.build_from_stage else None,
        )
