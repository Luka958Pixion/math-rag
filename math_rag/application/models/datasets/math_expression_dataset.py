from pydantic import RootModel

from .math_expression_sample import MathExpressionSample


class MathExpressionDataset(RootModel[list[MathExpressionSample]]):
    pass
