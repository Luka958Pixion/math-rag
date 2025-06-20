from uuid import UUID

from pydantic import BaseModel

from math_rag.core.enums import MathExpressionDatasetBuildPriority, MathExpressionDatasetBuildStage
from math_rag.core.models import MathExpressionDatasetBuildDetails


class Request(BaseModel):
    build_from_id: UUID | None
    build_from_stage: MathExpressionDatasetBuildStage | None
    build_priority: MathExpressionDatasetBuildPriority
    build_details: MathExpressionDatasetBuildDetails
