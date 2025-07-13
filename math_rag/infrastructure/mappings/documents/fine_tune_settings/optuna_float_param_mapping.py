from math_rag.core.models.fine_tune_settings import OptunaFloatParam
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents.fine_tune_settings import OptunaFloatParamDocument


class OptunaFloatParamMapping(BaseMapping[OptunaFloatParam, OptunaFloatParamDocument]):
    @staticmethod
    def to_source(target: OptunaFloatParamDocument) -> OptunaFloatParam:
        return OptunaFloatParam(
            name=target.name, low=target.low, high=target.high, step=target.step
        )

    @staticmethod
    def to_target(source: OptunaFloatParam) -> OptunaFloatParamDocument:
        return OptunaFloatParamDocument(
            name=source.name, low=source.low, high=source.high, step=source.step
        )
