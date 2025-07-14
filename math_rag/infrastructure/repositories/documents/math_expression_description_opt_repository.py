from pymongo import AsyncMongoClient

from math_rag.application.base.repositories.documents import (
    BaseMathExpressionDescriptionOptRepository,
)
from math_rag.core.models import MathExpressionDescriptionOpt
from math_rag.infrastructure.mappings.documents import MathExpressionDescriptionOptMapping
from math_rag.infrastructure.models.documents import MathExpressionDescriptionOptDocument

from .document_repository import DocumentRepository


class MathExpressionDescriptionOptRepository(
    BaseMathExpressionDescriptionOptRepository,
    DocumentRepository[
        MathExpressionDescriptionOpt,
        MathExpressionDescriptionOptDocument,
        MathExpressionDescriptionOptMapping,
    ],
):
    def __init__(self, client: AsyncMongoClient, deployment: str):
        super().__init__(client, deployment)
