from enum import Enum


class MathExpressionLabelEnum(str, Enum):
    EQUALITY = 'equality'
    INEQUALITY = 'inequality'
    CONSTANT = 'constant'
    VARIABLE = 'variable'
    OTHER = 'other'

    @classmethod
    def from_index(cls, index):
        return list(cls)[index]
