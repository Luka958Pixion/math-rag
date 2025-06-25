from math_rag.infrastructure.base import BaseDocument


class OptunaIntParamDocument(BaseDocument):
    name: str
    low: int
    high: int
    step: int
