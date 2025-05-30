from math_rag.core.base import BaseDataset
from math_rag.core.enums import MathExpressionDatasetBuildStage

from .math_expression_sample import MathExpressionSample


class MathExpressionDataset(BaseDataset[MathExpressionSample, MathExpressionDatasetBuildStage]):
    pass
