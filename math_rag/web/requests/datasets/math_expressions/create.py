from uuid import UUID

from pydantic import BaseModel

from math_rag.core.enums import MathExpressionDatasetBuildPriority, MathExpressionDatasetBuildStage
from math_rag.core.models import DatasetSplits
from math_rag.core.types.arxiv import ArxivCategoryEnum, ArxivCategoryUnion


class MathExpressionDatasetBuildDetails(BaseModel):
    arxiv_category_type: ArxivCategoryEnum | None
    arxiv_category: ArxivCategoryUnion | None
    splits: DatasetSplits


class MathExpressionDatasetCreateRequest(BaseModel):
    build_from_id: UUID | None
    build_from_stage: MathExpressionDatasetBuildStage | None
    build_priority: MathExpressionDatasetBuildPriority
    build_details: MathExpressionDatasetBuildDetails
