from pymongo import AsyncMongoClient

from math_rag.application.base.repositories.documents import (
    BaseMathExpressionClassificationRepository,
)
from math_rag.core.models import MathExpressionClassification
from math_rag.infrastructure.mappings.documents import (
    MathExpressionClassificationMapping,
)
from math_rag.infrastructure.models.documents import (
    MathExpressionClassificationDocument,
)

from .document_repository import DocumentRepository


class MathExpressionClassificationRepository(
    BaseMathExpressionClassificationRepository,
    DocumentRepository[
        MathExpressionClassification,
        MathExpressionClassificationDocument,
        MathExpressionClassificationMapping,
    ],
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
