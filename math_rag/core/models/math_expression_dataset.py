from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.core.enums import DatasetBuildStatus, MathExpressionDatasetBuildStage

from .math_expression_sample import MathExpressionSample


class MathExpressionDataset(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.now)
    build_stage: MathExpressionDatasetBuildStage
    build_status: DatasetBuildStatus
    build_from_dataset_id: UUID | None = None
    build_from_stage: MathExpressionDatasetBuildStage | None = None
