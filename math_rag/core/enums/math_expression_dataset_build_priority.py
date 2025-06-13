from enum import Enum


class MathExpressionDatasetBuildPriority(str, Enum):
    COST = 'cost'
    TIME = 'time'
