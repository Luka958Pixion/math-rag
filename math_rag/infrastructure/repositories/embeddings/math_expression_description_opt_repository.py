from qdrant_client import AsyncQdrantClient

from math_rag.application.base.repositories.embeddings import (
    BaseMathExpressionDescriptionOptRepository,
)
from math_rag.core.models import MathExpressionDescriptionOpt
from math_rag.infrastructure.mappings.embeddings import MathExpressionDescriptionOptMapping
from math_rag.infrastructure.models.embeddings import (
    MathExpressionDescriptionOptEmbedding,
)

from .embedding_repository import EmbeddingRepository


class MathExpressionDescriptionOptRepository(
    BaseMathExpressionDescriptionOptRepository,
    EmbeddingRepository[
        MathExpressionDescriptionOpt,
        MathExpressionDescriptionOptEmbedding,
        MathExpressionDescriptionOptMapping,
    ],
):
    def __init__(self, client: AsyncQdrantClient):
        super().__init__(client)
