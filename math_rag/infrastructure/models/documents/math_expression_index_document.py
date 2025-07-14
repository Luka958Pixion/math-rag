from datetime import datetime
from pathlib import Path
from uuid import UUID

from math_rag.infrastructure.base import BaseDocument


class MathExpressionIndexDocument(BaseDocument):
    id: UUID
    timestamp: datetime
    build_stage: str

    # NOTE: build_details are flattened
    file_path: Path
