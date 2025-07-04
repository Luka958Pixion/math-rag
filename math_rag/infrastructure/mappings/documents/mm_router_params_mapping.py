from math_rag.application.enums.inference import MMInferenceProvider, MMModelProvider
from math_rag.application.models.inference import MMRouterParams
from math_rag.infrastructure.base import BaseMapping
from math_rag.infrastructure.models.documents import MMRouterParamsDocument


class MMRouterParamsMapping(BaseMapping[MMRouterParams, MMRouterParamsDocument]):
    @staticmethod
    def to_source(target: MMRouterParamsDocument) -> MMRouterParams:
        return MMRouterParams(
            id=target.id,
            inference_provider=MMInferenceProvider(target.inference_provider),
            model_provider=MMModelProvider(target.model_provider),
        )

    @staticmethod
    def to_target(source: MMRouterParams) -> MMRouterParamsDocument:
        return MMRouterParamsDocument(
            id=source.id,
            inference_provider=source.inference_provider.value,
            model_provider=source.model_provider.value,
        )
