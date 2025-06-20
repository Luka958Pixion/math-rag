from datetime import datetime
from uuid import UUID

from math_rag.infrastructure.base import BaseDocument

from .math_expression_label_document import MathExpressionLabelDocument


class MathExpressionDatasetTestResultDocument(BaseDocument):
    id: UUID
    math_expression_dataset_test_id: UUID
    math_expression_labels: list[MathExpressionLabelDocument]
    timestamp: datetime
