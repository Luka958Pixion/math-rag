from math_rag.application.models.inference import EMParams
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import EMParamsDocument


class EMParamsMapping(BaseMapping[EMParams, EMParamsDocument]):
    @staticmethod
    def to_source(target: EMParamsDocument) -> EMParams:
        return EMParams(id=target.id, model=target.model, dimensions=target.dimensions)

    @staticmethod
    def to_target(source: EMParams) -> EMParamsDocument:
        return EMParamsDocument(id=source.id, model=source.model, dimensions=source.dimensions)
