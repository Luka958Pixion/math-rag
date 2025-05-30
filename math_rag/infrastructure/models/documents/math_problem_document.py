from datetime import datetime
from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class MathProblemDocument(BaseDocument):
    id: UUID
    timestamp: datetime
    latex: str
    katex: str | None
    is_inline: bool
