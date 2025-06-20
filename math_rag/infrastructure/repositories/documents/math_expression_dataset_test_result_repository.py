from pymongo import AsyncMongoClient

from math_rag.application.base.repositories.documents import (
    BaseMathExpressionDatasetTestResultRepository,
)
from math_rag.core.models import MathExpressionDatasetTestResult
from math_rag.infrastructure.mappings.documents import MathExpressionDatasetTestResultMapping
from math_rag.infrastructure.models.documents import MathExpressionDatasetTestResultDocument

from .document_repository import DocumentRepository


class MathExpressionDatasetTestResultRepository(
    BaseMathExpressionDatasetTestResultRepository,
    DocumentRepository[
        MathExpressionDatasetTestResult,
        MathExpressionDatasetTestResultDocument,
        MathExpressionDatasetTestResultMapping,
    ],
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
