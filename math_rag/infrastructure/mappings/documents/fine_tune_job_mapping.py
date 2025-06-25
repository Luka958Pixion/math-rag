from math_rag.core.models import FineTuneJob
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import FineTuneJobDocument


class FineTuneJobMapping(BaseMapping[FineTuneJob, FineTuneJobDocument]):
    @staticmethod
    def to_source(target: FineTuneJobDocument) -> FineTuneJob:
        return FineTuneJob.model_validate(target.model_dump())

    @staticmethod
    def to_target(source: FineTuneJob) -> FineTuneJobDocument:
        return FineTuneJobDocument.model_validate(source.model_dump())
