from math_rag.application.base.inference import BaseBasicEM, BaseBasicManagedEM
from math_rag.application.models.inference import (
    EMRequest,
    EMResult,
)


class OpenAIBasicManagedEM(BaseBasicManagedEM):
    def __init__(self, em: BaseBasicEM):
        self.em = em

    async def embed(self, request: EMRequest) -> EMResult:
        return await self.em.embed(
            request,
            max_time=...,
            max_num_retries=...,  # TODO
        )
