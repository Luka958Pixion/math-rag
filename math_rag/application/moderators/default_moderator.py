from uuid import UUID

from math_rag.application.base.inference import BaseManagedMM
from math_rag.application.enums.inference import MMInferenceProvider, MMModelProvider
from math_rag.application.models.inference import (
    MMParams,
    MMRequest,
    MMResponseList,
    MMRouterParams,
)
from math_rag.application.models.moderators import ModeratorInput, ModeratorOutput

from .partials import PartialModerator


class DefaultModerator(PartialModerator[ModeratorInput, ModeratorOutput]):
    def __init__(self, mm: BaseManagedMM):
        super().__init__(mm)

        self._request_id_to_input_id: dict[UUID, UUID] = {}

    def encode_to_request(self, input: ModeratorInput) -> MMRequest:
        request = MMRequest(
            text=input.text,
            params=MMParams(model='omni-moderation-latest'),
            router_params=MMRouterParams(
                inference_provider=MMInferenceProvider.OPEN_AI,
                model_provider=MMModelProvider.OPEN_AI,
            ),
        )
        self._request_id_to_input_id[request.id] = input.id

        return request

    def decode_from_response_list(self, response_list: MMResponseList) -> ModeratorOutput:
        # NOTE: this method won't be called if the request has failed,
        # so an item from dict won't be popped, but this is not a problem
        # because this class is a factory so it won't fill up the memory
        return ModeratorOutput(
            input_id=self._request_id_to_input_id.pop(response_list.request_id),
            is_flagged=any(
                category.is_flagged for category in response_list.responses[0].categories
            ),
        )
