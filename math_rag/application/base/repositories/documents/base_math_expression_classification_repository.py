from math_rag.core.models import MathExpressionClassification

from .base_document_repository import BaseDocumentRepository


class BaseMathExpressionClassificationRepository(
    BaseDocumentRepository[MathExpressionClassification]
):
    pass
