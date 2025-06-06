from typing import cast

from math_rag.application.base.assistants import BaseAssistantProtocol, BaseConcurrentAssistant
from math_rag.application.base.inference import BaseConcurrentManagedEM
from math_rag.application.models.inference import EMConcurrentRequest
from math_rag.application.types.embedants import EmbedantInputType, EmbedantOutputType
from math_rag.shared.utils import TypeUtil


class PartialConcurrentEmbedant(
    BaseConcurrentAssistant[EmbedantInputType, EmbedantOutputType],
    BaseAssistantProtocol[EmbedantInputType, EmbedantOutputType],
):
    def __init__(self, em: BaseConcurrentManagedEM):
        self._em = em

        args = TypeUtil.get_type_args(self.__class__)
        self._response_type = cast(type[EmbedantOutputType], args[0][1])

    async def concurrent_assist(
        self,
        inputs: list[EmbedantInputType],
    ) -> list[EmbedantOutputType]:
        concurrent_request = EMConcurrentRequest(
            requests=[self.encode_to_request(input) for input in inputs]
        )
        concurrent_result = await self._em.concurrent_embed(concurrent_request)
        outputs = [
            self.decode_from_response_list(response_list)
            for response_list in concurrent_result.response_lists
        ]

        return outputs
