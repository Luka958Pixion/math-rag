from pymongo import AsyncMongoClient

from math_rag.application.base.repositories.documents import (
    BaseMathExpressionLabelRepository,
)
from math_rag.core.models import MathExpressionLabel
from math_rag.infrastructure.mappings.documents import (
    MathExpressionLabelMapping,
)
from math_rag.infrastructure.models.documents import (
    MathExpressionLabelDocument,
)

from .document_repository import DocumentRepository


class MathExpressionLabelRepository(
    BaseMathExpressionLabelRepository,
    DocumentRepository[
        MathExpressionLabel,
        MathExpressionLabelDocument,
        MathExpressionLabelMapping,
    ],
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
