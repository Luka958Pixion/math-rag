from math_rag.core.models.fine_tune_settings import OptunaIntParam
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents.fine_tune_settings import OptunaIntParamDocument


class OptunaIntParamMapping(BaseMapping[OptunaIntParam, OptunaIntParamDocument]):
    @staticmethod
    def to_source(target: OptunaIntParamDocument) -> OptunaIntParam:
        return OptunaIntParam.model_validate(target.model_dump())

    @staticmethod
    def to_target(source: OptunaIntParam) -> OptunaIntParamDocument:
        return OptunaIntParamDocument.model_validate(source.model_dump())
