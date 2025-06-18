from datetime import datetime
from uuid import UUID, uuid4

from pydantic import Field

from math_rag.core.base import BaseLabelTask


class MathExpressionLabelTask(BaseLabelTask):
    id: UUID = Field(default_factory=uuid4)
    math_expression_id: UUID
    math_expression_dataset_id: UUID
    timestamp: datetime = Field(default_factory=datetime.now)
    katex: str
    html: str
