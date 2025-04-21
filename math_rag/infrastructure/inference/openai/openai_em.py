from openai import AsyncOpenAI

from .openai_basic_em import OpenAIBasicEM
from .openai_batch_em import OpenAIBatchEM
from .openai_concurrent_em import OpenAIConcurrentEM


class OpenAIEM(OpenAIBasicEM, OpenAIBatchEM, OpenAIConcurrentEM):
    def __init__(self, client: AsyncOpenAI):
        OpenAIBasicEM.__init__(self, client)
        OpenAIBatchEM.__init__(self, client)
        OpenAIConcurrentEM.__init__(self, client)
