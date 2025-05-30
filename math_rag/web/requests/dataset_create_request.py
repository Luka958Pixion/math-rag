from uuid import UUID

from pydantic import BaseModel

from math_rag.core.enums import MathExpressionDatasetBuildStage


class DatasetCreateRequest(BaseModel):
    build_from_index_id: UUID | None
    build_from_stage: MathExpressionDatasetBuildStage | None
