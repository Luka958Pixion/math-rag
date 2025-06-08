from uuid import UUID

from math_rag.application.base.inference import (
    BaseBatchEMRequestManagedScheduler,
    BaseManagedEM,
)
from math_rag.application.models.embedants import EmbedantInput, EmbedantOutput
from math_rag.application.models.inference import (
    EMParams,
    EMRequest,
    EMResponseList,
)

from .partials import PartialEmbedant


class MathExpressionDescriptionEmbedant(PartialEmbedant[EmbedantInput, EmbedantOutput]):
    def __init__(self, em: BaseManagedEM, scheduler: BaseBatchEMRequestManagedScheduler | None):
        super().__init__(em, scheduler)

        self._request_id_to_input_id: dict[UUID, UUID] = {}

    def encode_to_request(self, input: EmbedantInput) -> EMRequest:
        request = EMRequest(
            text=input.text,
            params=EMParams(model='text-embedding-3-small', dimensions=1536),
        )
        self._request_id_to_input_id[request.id] = input.id

        return request

    def decode_from_response_list(self, response_list: EMResponseList) -> EmbedantOutput:
        # NOTE: this method won't be called if the request has failed,
        # so an item from dict won't be popped, but this is not a problem
        # because this class is a factory so it won't fill up the memory
        return EmbedantOutput(
            input_id=self._request_id_to_input_id.pop(response_list.request_id),
            embedding=response_list.responses[0].embedding,
        )
