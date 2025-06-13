from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from math_rag.core.enums import (
    MathExpressionDatasetBuildPriority,
    MathExpressionDatasetBuildStage,
    MathExpressionDatasetBuildStatus,
)
from math_rag.core.models import MathExpressionDatasetBuildDetails


class MathExpressionDatasetCreateResponse(BaseModel):
    id: UUID
    timestamp: datetime
    build_stage: MathExpressionDatasetBuildStage
    build_status: MathExpressionDatasetBuildStatus
    build_from_id: UUID | None
    build_from_stage: MathExpressionDatasetBuildStage | None
    build_priority: MathExpressionDatasetBuildPriority
    build_details: MathExpressionDatasetBuildDetails
