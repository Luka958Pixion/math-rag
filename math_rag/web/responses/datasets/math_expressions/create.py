from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from math_rag.core.enums import MathExpressionDatasetBuildStage, MathExpressionDatasetBuildStatus


class MathExpressionDatasetCreateResponse(BaseModel):
    id: UUID
    timestamp: datetime
    build_stage: MathExpressionDatasetBuildStage
    build_status: MathExpressionDatasetBuildStatus
    build_from_dataset_id: UUID | None
    build_from_stage: MathExpressionDatasetBuildStage | None
