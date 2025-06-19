from math_rag.core.models import FineTuneJob
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import FineTuneJobDocument


class FineTuneJobMapping(BaseMapping[FineTuneJob, FineTuneJobDocument]):
    @staticmethod
    def to_source(target: FineTuneJobDocument) -> FineTuneJob:
        return FineTuneJob(
            id=target.id,
            timestamp=target.timestamp,
            provider_name=target.provider_name,
            model_name=target.model_name,
        )

    @staticmethod
    def to_target(source: FineTuneJob) -> FineTuneJobDocument:
        return FineTuneJobDocument(
            id=source.id,
            timestamp=source.timestamp,
            provider_name=source.provider_name,
            model_name=source.model_name,
        )
