from math_rag.infrastructure.base import BaseDocument


class OptunaFloatParamDocument(BaseDocument):
    name: str
    low: float
    high: float
    step: float
