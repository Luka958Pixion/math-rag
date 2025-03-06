from enum import Enum


class MathExpressionCategory(str, Enum):
    EQUALITY = 'equality'
    INEQUALITY = 'inequality'
    CONSTANT = 'constant'
    VARIABLE = 'variable'
    OTHER = 'other'
