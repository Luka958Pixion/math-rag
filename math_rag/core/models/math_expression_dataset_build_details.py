from pydantic import BaseModel, model_validator

from math_rag.core.models import DatasetSplit
from math_rag.core.types.arxiv import ArxivCategoryType


class MathExpressionDatasetBuildDetails(BaseModel):
    arxiv_category_type: type[ArxivCategoryType] | None
    arxiv_category: ArxivCategoryType | None
    splits: list[DatasetSplit]

    @model_validator(mode='after')
    def check_category_fields(self) -> 'MathExpressionDatasetBuildDetails':
        if self.arxiv_category_type is None and self.arxiv_category is None:
            raise ValueError('Either arxiv_category_type or arxiv_category must be provided')

        return self
