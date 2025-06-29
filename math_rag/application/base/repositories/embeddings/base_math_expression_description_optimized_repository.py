from math_rag.core.models import MathExpressionDescription

from .base_embedding_repository import BaseEmbeddingRepository


class BaseMathExpressionDescriptionOptimizedRepository(
    BaseEmbeddingRepository[MathExpressionDescription]
):
    pass
