from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from math_rag.core.enums import (
    MathExpressionDatasetBuildPriority,
    MathExpressionDatasetBuildStage,
    TaskStatus,
)
from math_rag.core.models import MathExpressionDatasetBuildDetails


class MathExpressionDatasetCreateResponse(BaseModel):
    id: UUID
    timestamp: datetime
    build_stage: MathExpressionDatasetBuildStage
    task_status: TaskStatus
    build_from_id: UUID | None
    build_from_stage: MathExpressionDatasetBuildStage | None
    build_priority: MathExpressionDatasetBuildPriority
    build_details: MathExpressionDatasetBuildDetails
