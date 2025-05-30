from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from math_rag.core.enums import DatasetBuildStatus, MathExpressionDatasetBuildStage


class DatasetCreateResponse(BaseModel):
    id: UUID
    timestamp: datetime
    build_stage: MathExpressionDatasetBuildStage
    build_status: DatasetBuildStatus
    build_from_index_id: UUID | None
    build_from_stage: MathExpressionDatasetBuildStage | None
