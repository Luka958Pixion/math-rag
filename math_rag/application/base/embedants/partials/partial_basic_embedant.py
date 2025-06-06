from math_rag.application.base.assistants import BaseAssistantProtocol, BaseBasicAssistant
from math_rag.application.base.inference import BaseBasicManagedEM
from math_rag.application.types.embedants import EmbedantInputType, EmbedantOutputType


class PartialBasicEmbedant(
    BaseBasicAssistant[EmbedantInputType, EmbedantOutputType],
    BaseAssistantProtocol[EmbedantInputType, EmbedantOutputType],
):
    def __init__(self, em: BaseBasicManagedEM):
        self._em = em

    async def assist(self, input: EmbedantInputType) -> EmbedantOutputType | None:
        request = self.encode_to_request(input)
        result = await self._em.embed(request)

        if result.failed_request:
            return None

        output = self.decode_from_response_list(result.response_list)

        return output
