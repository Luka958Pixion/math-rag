from math_rag.application.base.embedders import BaseConcurrentEmbedder, BaseEmbedderProtocol
from math_rag.application.base.inference import BaseConcurrentManagedEM
from math_rag.application.models.inference import EMConcurrentRequest
from math_rag.application.types.embedders import EmbedderInputType, EmbedderOutputType


class PartialConcurrentEmbedder(
    BaseConcurrentEmbedder[EmbedderInputType, EmbedderOutputType],
    BaseEmbedderProtocol[EmbedderInputType, EmbedderOutputType],
):
    def __init__(self, em: BaseConcurrentManagedEM):
        self._em = em

    async def concurrent_embed(
        self,
        inputs: list[EmbedderInputType],
    ) -> list[EmbedderOutputType]:
        concurrent_request = EMConcurrentRequest(
            requests=[self.encode_to_request(input) for input in inputs]
        )
        concurrent_result = await self._em.concurrent_embed(concurrent_request)
        outputs = [
            self.decode_from_response_list(response_list)
            for response_list in concurrent_result.response_lists
        ]

        return outputs
