from uuid import UUID

from pydantic import BaseModel

from math_rag.application.types.arxiv import ArxivCategoryTypeEnum, ArxivCategoryUnionType
from math_rag.core.enums import MathExpressionDatasetBuildStage
from math_rag.core.models import DatasetSplits


class MathExpressionDatasetCreateRequest(BaseModel):
    build_from_id: UUID | None
    build_from_stage: MathExpressionDatasetBuildStage | None

    arxiv_category_type: ArxivCategoryTypeEnum | None = None
    arxiv_category: ArxivCategoryUnionType | None = None
    splits: DatasetSplits
