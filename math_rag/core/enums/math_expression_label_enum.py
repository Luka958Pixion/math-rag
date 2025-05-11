from enum import Enum


class MathExpressionLabelEnum(str, Enum):
    EQUALITY = 'equality'
    INEQUALITY = 'inequality'
    CONSTANT = 'constant'
    VARIABLE = 'variable'
    OTHER = 'other'
