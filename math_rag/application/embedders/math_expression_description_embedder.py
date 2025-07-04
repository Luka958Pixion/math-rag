from uuid import UUID

from math_rag.application.base.inference import BaseBatchEMRequestManagedScheduler, BaseManagedEM
from math_rag.application.enums.inference import EMInferenceProvider, EMModelProvider
from math_rag.application.models.embedders import EmbedderInput, EmbedderOutput
from math_rag.application.models.inference import (
    EMParams,
    EMRequest,
    EMResponseList,
    EMRouterParams,
)

from .partials import PartialEmbedder


class MathExpressionDescriptionEmbedder(PartialEmbedder[EmbedderInput, EmbedderOutput]):
    def __init__(self, em: BaseManagedEM, scheduler: BaseBatchEMRequestManagedScheduler | None):
        super().__init__(em, scheduler)

        self._request_id_to_input_id: dict[UUID, UUID] = {}

    def encode_to_request(self, input: EmbedderInput) -> EMRequest:
        request = EMRequest(
            text=input.text,
            params=EMParams(
                model='text-embedding-3-small',
                dimensions=1536,
            ),
            router_params=EMRouterParams(
                inference_provider=EMInferenceProvider.OPEN_AI,
                model_provider=EMModelProvider.OPEN_AI,
            ),
        )
        self._request_id_to_input_id[request.id] = input.id

        return request

    def decode_from_response_list(self, response_list: EMResponseList) -> EmbedderOutput:
        # NOTE: this method won't be called if the request has failed,
        # so an item from dict won't be popped, but this is not a problem
        # because this class is a factory so it won't fill up the memory
        return EmbedderOutput(
            input_id=self._request_id_to_input_id.pop(response_list.request_id),
            embedding=response_list.responses[0].embedding,
        )
