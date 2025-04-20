from openai import AsyncOpenAI

from .openai_batch_managed_em import OpenAIBatchManagedEM
from .openai_concurrent_managed_em import OpenAIConcurrentManagedEM
from .openai_managed_em import OpenAIManagedEM


class OpenAIUnifiedManagedEM(
    OpenAIManagedEM, OpenAIBatchManagedEM, OpenAIConcurrentManagedEM
):
    def __init__(self, client: AsyncOpenAI):
        OpenAIManagedEM.__init__(self, client)
        OpenAIBatchManagedEM.__init__(self, client)
        OpenAIConcurrentManagedEM.__init__(self, client)
