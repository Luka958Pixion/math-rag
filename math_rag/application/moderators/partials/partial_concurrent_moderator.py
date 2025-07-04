from math_rag.application.base.inference import BaseConcurrentManagedMM
from math_rag.application.base.moderators import BaseConcurrentModerator, BaseModeratorProtocol
from math_rag.application.models.inference import MMConcurrentRequest
from math_rag.application.types.moderators import ModeratorInputType, ModeratorOutputType


class PartialConcurrentModerator(
    BaseConcurrentModerator[ModeratorInputType, ModeratorOutputType],
    BaseModeratorProtocol[ModeratorInputType, ModeratorOutputType],
):
    def __init__(self, mm: BaseConcurrentManagedMM):
        self._mm = mm

    async def concurrent_moderate(
        self,
        inputs: list[ModeratorInputType],
    ) -> list[ModeratorOutputType]:
        concurrent_request = MMConcurrentRequest(
            requests=[self.encode_to_request(input) for input in inputs]
        )
        concurrent_result = await self._mm.concurrent_moderate(concurrent_request)

        return [
            self.decode_from_response_list(response_list)
            for response_list in concurrent_result.response_lists
        ]
