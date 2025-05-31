from pydantic import Field

from math_rag.core.enums import MathExpressionDatasetBuildStage

from .dataset import Dataset


class MathExpressionDataset(Dataset):
    build_stage: MathExpressionDatasetBuildStage = Field(
        default=MathExpressionDatasetBuildStage.LOAD_MATH_ARTICLES
    )
    build_from_stage: MathExpressionDatasetBuildStage | None = None
