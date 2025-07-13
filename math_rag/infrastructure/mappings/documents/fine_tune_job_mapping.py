from math_rag.core.models import FineTuneJob
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import FineTuneJobDocument


class FineTuneJobMapping(BaseMapping[FineTuneJob, FineTuneJobDocument]):
    @staticmethod
    def to_source(target: FineTuneJobDocument) -> FineTuneJob:
        return FineTuneJob(
            id=target.id, timestamp=target.timestamp, fine_tune_settings=target.fine_tune_settings
        )

    @staticmethod
    def to_target(source: FineTuneJob) -> FineTuneJobDocument:
        return FineTuneJobDocument(
            id=source.id, timestamp=source.timestamp, fine_tune_settings=source.fine_tune_settings
        )
