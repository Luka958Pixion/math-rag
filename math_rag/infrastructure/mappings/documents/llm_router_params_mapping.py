from math_rag.application.enums.inference import LLMInferenceProvider, LLMModelProvider
from math_rag.application.models.inference import LLMRouterParams
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import LLMRouterParamsDocument


class LLMRouterParamsMapping(BaseMapping[LLMRouterParams, LLMRouterParamsDocument]):
    @staticmethod
    def to_source(target: LLMRouterParamsDocument) -> LLMRouterParams:
        return LLMRouterParams(
            id=target.id,
            inference_provider=LLMInferenceProvider(target.inference_provider),
            model_provider=LLMModelProvider(target.model_provider),
        )

    @staticmethod
    def to_target(source: LLMRouterParams) -> LLMRouterParamsDocument:
        return LLMRouterParamsDocument(
            id=source.id,
            inference_provider=source.inference_provider.value,
            model_provider=source.model_provider.value,
        )
