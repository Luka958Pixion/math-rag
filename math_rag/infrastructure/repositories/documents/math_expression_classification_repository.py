from pymongo import AsyncMongoClient

from math_rag.core.models import MathExpressionClassification
from math_rag.infrastructure.mappings.documents import (
    MathExpressionClassificationMapping,
)
from math_rag.infrastructure.models.documents import (
    MathExpressionClassificationDocument,
)

from .document_repository import DocumentRepository


class MathExpressionClassificationRepository(
    DocumentRepository[
        MathExpressionClassification,
        MathExpressionClassificationDocument,
        MathExpressionClassificationMapping,
    ]
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
