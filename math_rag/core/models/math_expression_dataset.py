from pydantic import Field, model_validator

from math_rag.core.base import BaseDataset
from math_rag.core.enums import (
    MathExpressionDatasetBuildPriority,
    MathExpressionDatasetBuildStage,
    MathExpressionDatasetBuildStatus,
)

from .math_expression_dataset_build_details import MathExpressionDatasetBuildDetails


class MathExpressionDataset(BaseDataset):
    build_status: MathExpressionDatasetBuildStatus = Field(
        default=MathExpressionDatasetBuildStatus.PENDING
    )
    build_stage: MathExpressionDatasetBuildStage = Field(
        default=MathExpressionDatasetBuildStage.LOAD_MATH_ARTICLES
    )
    build_from_stage: MathExpressionDatasetBuildStage | None = None
    build_priority: MathExpressionDatasetBuildPriority
    build_details: MathExpressionDatasetBuildDetails

    @model_validator(mode='after')
    def check_build_from(self):
        if (self.build_from_id is None) != (self.build_from_stage is None):
            raise ValueError(
                'Either both build_from_id and build_from_stage must be set, or neither'
            )

        return self
