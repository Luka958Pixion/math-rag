from uuid import UUID

from pydantic import BaseModel

from math_rag.core.enums import MathExpressionDatasetBuildStage


class MathExpressionDatasetCreateRequest(BaseModel):
    build_from_dataset_id: UUID | None
    build_from_stage: MathExpressionDatasetBuildStage | None
