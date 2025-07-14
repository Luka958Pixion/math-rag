from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.core.enums import MathExpressionIndexBuildStage
from math_rag.core.models import MathExpressionIndexBuildDetails


class MathExpressionIndex(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.now)
    build_stage: MathExpressionIndexBuildStage = Field(
        default=MathExpressionIndexBuildStage.LOAD_MATH_ARTICLES
    )
    build_details: MathExpressionIndexBuildDetails
