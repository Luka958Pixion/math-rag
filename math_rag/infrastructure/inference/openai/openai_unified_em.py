from openai import AsyncOpenAI

from .openai_batch_em import OpenAIBatchEM
from .openai_concurrent_em import OpenAIConcurrentEM
from .openai_em import OpenAIEM


class OpenAIUnifiedEM(OpenAIEM, OpenAIBatchEM, OpenAIConcurrentEM):
    def __init__(self, client: AsyncOpenAI):
        OpenAIEM.__init__(self, client)
        OpenAIBatchEM.__init__(self, client)
        OpenAIConcurrentEM.__init__(self, client)
