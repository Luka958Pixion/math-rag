from datetime import datetime
from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class MathProblemSolutionDocument(BaseDocument):
    id: UUID
    timestamp: datetime
