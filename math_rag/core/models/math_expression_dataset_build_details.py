from pydantic import BaseModel

from math_rag.core.models import DatasetSplit
from math_rag.core.types import ArxivCategoryType


class MathExpressionDatasetBuildDetails(BaseModel):
    categories: list[ArxivCategoryType]
    category_limit: int
    splits: list[DatasetSplit]
