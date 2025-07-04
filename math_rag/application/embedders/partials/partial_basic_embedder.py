from math_rag.application.base.embedders import BaseBasicEmbedder, BaseEmbedderProtocol
from math_rag.application.base.inference import BaseBasicManagedEM
from math_rag.application.types.embedders import EmbedderInputType, EmbedderOutputType


class PartialBasicEmbedder(
    BaseBasicEmbedder[EmbedderInputType, EmbedderOutputType],
    BaseEmbedderProtocol[EmbedderInputType, EmbedderOutputType],
):
    def __init__(self, em: BaseBasicManagedEM):
        self._em = em

    async def embed(self, input: EmbedderInputType) -> EmbedderOutputType | None:
        request = self.encode_to_request(input)
        result = await self._em.embed(request)

        if result.failed_request:
            return None

        output = self.decode_from_response_list(result.response_list)

        return output
