from pymongo import AsyncMongoClient

from math_rag.application.base.repositories.documents import (
    BaseMathExpressionRelationshipDescriptionRepository,
)
from math_rag.core.models import MathExpressionRelationshipDescription
from math_rag.infrastructure.mappings.documents import MathExpressionRelationshipDescriptionMapping
from math_rag.infrastructure.models.documents import MathExpressionRelationshipDescriptionDocument

from .document_repository import DocumentRepository


class MathExpressionRelationshipDescriptionRepository(
    BaseMathExpressionRelationshipDescriptionRepository,
    DocumentRepository[
        MathExpressionRelationshipDescription,
        MathExpressionRelationshipDescriptionDocument,
        MathExpressionRelationshipDescriptionMapping,
    ],
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
