from pymongo import AsyncMongoClient

from math_rag.application.base.repositories.documents import (
    BaseMathExpressionDescriptionRepository,
)
from math_rag.core.models import MathExpressionDescription
from math_rag.infrastructure.mappings.documents import MathExpressionDescriptionMapping
from math_rag.infrastructure.models.documents import MathExpressionDescriptionDocument

from .document_repository import DocumentRepository


class MathExpressionDescriptionRepository(
    BaseMathExpressionDescriptionRepository,
    DocumentRepository[
        MathExpressionDescription,
        MathExpressionDescriptionDocument,
        MathExpressionDescriptionMapping,
    ],
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
