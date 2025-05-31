from math_rag.core.enums import DatasetBuildStatus, MathExpressionDatasetBuildStage
from math_rag.core.models import MathExpressionDataset
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MathExpressionDatasetDocument


class MathExpressionDatasetMapping(
    BaseMapping[MathExpressionDataset, MathExpressionDatasetDocument]
):
    @staticmethod
    def to_source(target: MathExpressionDatasetDocument) -> MathExpressionDataset:
        return MathExpressionDataset(
            id=target.id,
            timestamp=target.timestamp,
            build_stage=MathExpressionDatasetBuildStage(target.build_stage),
            build_status=DatasetBuildStatus(target.build_status),
            build_from_dataset_id=target.build_from_dataset_id,
            build_from_stage=MathExpressionDatasetBuildStage(target.build_from_stage)
            if target.build_from_stage
            else None,
        )

    @staticmethod
    def to_target(source: MathExpressionDataset) -> MathExpressionDatasetDocument:
        return MathExpressionDatasetDocument(
            id=source.id,
            timestamp=source.timestamp,
            build_stage=source.build_stage.value,
            build_status=source.build_status.value,
            build_from_dataset_id=source.build_from_dataset_id,
            build_from_stage=source.build_from_stage.value if source.build_from_stage else None,
        )
