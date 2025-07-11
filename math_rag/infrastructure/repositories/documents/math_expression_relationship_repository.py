from pymongo import AsyncMongoClient

from math_rag.application.base.repositories.documents import (
    BaseMathExpressionRelationshipRepository,
)
from math_rag.core.models import MathExpressionRelationship
from math_rag.infrastructure.mappings.documents import MathExpressionRelationshipMapping
from math_rag.infrastructure.models.documents import MathExpressionRelationshipDocument

from .document_repository import DocumentRepository


class MathExpressionRelationshipRepository(
    BaseMathExpressionRelationshipRepository,
    DocumentRepository[
        MathExpressionRelationship,
        MathExpressionRelationshipDocument,
        MathExpressionRelationshipMapping,
    ],
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
