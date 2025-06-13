from math_rag.core.enums import (
    MathExpressionDatasetBuildPriority,
    MathExpressionDatasetBuildStage,
    MathExpressionDatasetBuildStatus,
)
from math_rag.core.models import (
    DatasetSplit,
    MathExpressionDataset,
    MathExpressionDatasetBuildDetails,
)
from math_rag.core.types.arxiv import ArxivCategoryType
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
            build_status=MathExpressionDatasetBuildStatus(target.build_status),
            build_from_id=target.build_from_id,
            build_from_stage=MathExpressionDatasetBuildStage(target.build_from_stage)
            if target.build_from_stage
            else None,
            build_priority=MathExpressionDatasetBuildPriority(target.build_priority),
            build_details=MathExpressionDatasetBuildDetails(
                arxiv_category_type=TypeUtil[ArxivCategoryType].from_fqn(target.arxiv_category_type)
                if target.arxiv_category_type
                else None,
                arxiv_category=TypeUtil[ArxivCategoryType].from_fqn(target.arxiv_category[0])(
                    target.arxiv_category[1]
                )
                if target.arxiv_category
                else None,
                splits=[DatasetSplit(name=name, ratio=ratio) for name, ratio in target.splits],
            ),
        )

    @staticmethod
    def to_target(source: MathExpressionDataset) -> MathExpressionDatasetDocument:
        return MathExpressionDatasetDocument(
            id=source.id,
            timestamp=source.timestamp,
            build_stage=source.build_stage.value,
            build_status=source.build_status.value,
            build_from_id=source.build_from_id,
            build_from_stage=source.build_from_stage.value if source.build_from_stage else None,
            build_priority=source.build_priority.value,
            arxiv_category_type=TypeUtil.to_fqn(source.build_details.arxiv_category_type),
            arxiv_category=(
                TypeUtil.to_fqn(source.build_details.arxiv_category.__class__),
                source.build_details.arxiv_category.value,
            ),
            splits=[(split.name, split.ratio) for split in source.build_details.splits],
        )
