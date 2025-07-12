from uuid import UUID

from pymongo import AsyncMongoClient

from math_rag.application.base.repositories.documents import BaseMathExpressionContextRepository
from math_rag.core.models import MathExpressionContext
from math_rag.infrastructure.mappings.documents import MathExpressionContextMapping
from math_rag.infrastructure.models.documents import MathExpressionContextDocument

from .document_repository import DocumentRepository


class MathExpressionContextRepository(
    BaseMathExpressionContextRepository,
    DocumentRepository[
        MathExpressionContext, MathExpressionContextDocument, MathExpressionContextMapping
    ],
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
