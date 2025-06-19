from pymongo import AsyncMongoClient

from math_rag.application.base.repositories.documents import BaseMathExpressionDatasetTestRepository
from math_rag.core.models import MathExpressionDatasetTest
from math_rag.infrastructure.mappings.documents import MathExpressionDatasetTestMapping
from math_rag.infrastructure.models.documents import MathExpressionDatasetTestDocument

from .document_repository import DocumentRepository


class MathExpressionDatasetTestRepository(
    BaseMathExpressionDatasetTestRepository,
    DocumentRepository[
        MathExpressionDatasetTest,
        MathExpressionDatasetTestDocument,
        MathExpressionDatasetTestMapping,
    ],
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
