from pymongo import AsyncMongoClient

from math_rag.application.base.repositories.documents import BaseMathExpressionGroupRepository
from math_rag.core.models import MathExpressionGroup
from math_rag.infrastructure.mappings.documents import MathExpressionGroupMapping
from math_rag.infrastructure.models.documents import MathExpressionGroupDocument

from .document_repository import DocumentRepository


class MathExpressionGroupRepository(
    BaseMathExpressionGroupRepository,
    DocumentRepository[
        MathExpressionGroup, MathExpressionGroupDocument, MathExpressionGroupMapping
    ],
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
