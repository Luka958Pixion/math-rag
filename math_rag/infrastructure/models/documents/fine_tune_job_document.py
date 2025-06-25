from datetime import datetime
from uuid import UUID

from math_rag.infrastructure.base import BaseDocument

from .fine_tune_settings import FineTuneSettingsDocument


class FineTuneJobDocument(BaseDocument):
    id: UUID
    timestamp: datetime
    fine_tune_settings: FineTuneSettingsDocument
