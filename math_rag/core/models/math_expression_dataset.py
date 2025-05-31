from pydantic import Field

from math_rag.core.base import BaseDataset
from math_rag.core.enums import MathExpressionDatasetBuildStage, MathExpressionDatasetBuildStatus


class MathExpressionDataset(BaseDataset):
    build_status: MathExpressionDatasetBuildStatus = Field(
        default=MathExpressionDatasetBuildStatus.PENDING
    )
    build_stage: MathExpressionDatasetBuildStage = Field(
        default=MathExpressionDatasetBuildStage.LOAD_MATH_ARTICLES
    )
    build_from_stage: MathExpressionDatasetBuildStage | None = None
