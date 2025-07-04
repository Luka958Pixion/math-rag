from math_rag.application.models.inference import MMParams
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MMParamsDocument


class MMParamsMapping(BaseMapping[MMParams, MMParamsDocument]):
    @staticmethod
    def to_source(target: MMParamsDocument) -> MMParams:
        return MMParams(id=target.id, model=target.model)

    @staticmethod
    def to_target(source: MMParams) -> MMParamsDocument:
        return MMParamsDocument(id=source.id, model=source.model)
