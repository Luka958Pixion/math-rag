from math_rag.core.models import FineTuneJob

from .base_document_repository import BaseDocumentRepository
from .partials import BaseTaskTrackerRepository


class BaseFineTuneJobRepository(
    BaseDocumentRepository[FineTuneJob], BaseTaskTrackerRepository[FineTuneJob]
):
    pass
