from openai import AsyncOpenAI

from .openai_basic_managed_em import OpenAIBasicManagedEM
from .openai_batch_managed_em import OpenAIBatchManagedEM
from .openai_concurrent_managed_em import OpenAIConcurrentManagedEM


class OpenAIManagedEM(
    OpenAIBasicManagedEM, OpenAIBatchManagedEM, OpenAIConcurrentManagedEM
):
    def __init__(self, client: AsyncOpenAI):
        OpenAIBasicManagedEM.__init__(self, client)
        OpenAIBatchManagedEM.__init__(self, client)
        OpenAIConcurrentManagedEM.__init__(self, client)
