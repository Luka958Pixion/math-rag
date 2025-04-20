from math_rag.application.base.inference import BaseEM, BaseManagedEM
from math_rag.application.models.inference import (
    EMRequest,
    EMResult,
)


class OpenAIManagedEM(BaseManagedEM):
    def __init__(self, em: BaseEM):
        self.em = em

    async def embed(self, request: EMRequest) -> EMResult:
        return await self.em.embed(
            request,
            max_time=...,
            max_num_retries=...,  # TODO
        )
