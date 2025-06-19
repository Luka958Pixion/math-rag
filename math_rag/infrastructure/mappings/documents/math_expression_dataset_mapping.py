from math_rag.core.enums import (
    MathExpressionDatasetBuildPriority,
    MathExpressionDatasetBuildStage,
    TaskStatus,
)
from math_rag.core.models import (
    DatasetSplit,
    MathExpressionDataset,
    MathExpressionDatasetBuildDetails,
)
from math_rag.core.types import ArxivCategoryType
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MathExpressionDatasetDocument
from math_rag.shared.utils import TypeUtil


class MathExpressionDatasetMapping(
    BaseMapping[MathExpressionDataset, MathExpressionDatasetDocument]
):
    @staticmethod
    def to_source(target: MathExpressionDatasetDocument) -> MathExpressionDataset:
        return MathExpressionDataset(
            id=target.id,
            timestamp=target.timestamp,
            build_stage=MathExpressionDatasetBuildStage(target.build_stage),
            task_status=TaskStatus(target.task_status),
            build_from_id=target.build_from_id,
            build_from_stage=MathExpressionDatasetBuildStage(target.build_from_stage)
            if target.build_from_stage
            else None,
            build_priority=MathExpressionDatasetBuildPriority(target.build_priority),
            build_details=MathExpressionDatasetBuildDetails(
                categories=[
                    TypeUtil[ArxivCategoryType].from_fqn(fqn)(value)
                    for fqn, value in target.categories
                ],
                category_limit=target.category_limit,
                splits=[DatasetSplit(name=name, ratio=ratio) for name, ratio in target.splits],
            ),
        )

    @staticmethod
    def to_target(source: MathExpressionDataset) -> MathExpressionDatasetDocument:
        return MathExpressionDatasetDocument(
            id=source.id,
            timestamp=source.timestamp,
            build_stage=source.build_stage.value,
            task_status=source.task_status.value,
            build_from_id=source.build_from_id,
            build_from_stage=source.build_from_stage.value if source.build_from_stage else None,
            build_priority=source.build_priority.value,
            categories=[
                (TypeUtil[ArxivCategoryType].to_fqn(category.__class__), category.value)
                for category in source.build_details.categories
            ],
            category_limit=source.build_details.category_limit,
            splits=[(split.name, split.ratio) for split in source.build_details.splits],
        )
