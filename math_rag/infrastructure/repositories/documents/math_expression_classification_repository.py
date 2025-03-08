from pymongo import AsyncMongoClient

from math_rag.core.models import MathExpressionClassification
from math_rag.infrastructure.models.documents import (
    MathExpressionClassificationDocument,
)

from .common_repository import CommonRepository


class MathExpressionClassificationRepository(
    CommonRepository[MathExpressionClassificationDocument, MathExpressionClassification]
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
