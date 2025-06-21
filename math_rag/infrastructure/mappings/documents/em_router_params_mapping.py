from math_rag.application.enums.inference import EMInferenceProvider, EMModelProvider
from math_rag.application.models.inference import EMRouterParams
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import EMRouterParamsDocument


class EMRouterParamsMapping(BaseMapping[EMRouterParams, EMRouterParamsDocument]):
    @staticmethod
    def to_source(target: EMRouterParamsDocument) -> EMRouterParams:
        return EMRouterParams(
            id=target.id,
            inference_provider=EMInferenceProvider(target.inference_provider),
            model_provider=EMModelProvider(target.model_provider),
        )

    @staticmethod
    def to_target(source: EMRouterParams) -> EMRouterParamsDocument:
        return EMRouterParamsDocument(
            id=source.id,
            inference_provider=source.inference_provider.value,
            model_provider=source.model_provider.value,
        )
