from math_rag.application.base.inference import BaseBasicManagedMM
from math_rag.application.base.moderators import BaseBasicModerator, BaseModeratorProtocol
from math_rag.application.types.moderators import ModeratorInputType, ModeratorOutputType


class PartialBasicModerator(
    BaseBasicModerator[ModeratorInputType, ModeratorOutputType],
    BaseModeratorProtocol[ModeratorInputType, ModeratorOutputType],
):
    def __init__(self, mm: BaseBasicManagedMM):
        self._mm = mm

    async def moderate(self, input: ModeratorInputType) -> ModeratorOutputType | None:
        request = self.encode_to_request(input)
        result = await self._mm.moderate(request)

        if result.failed_request:
            return None

        return self.decode_from_response_list(result.response_list)
