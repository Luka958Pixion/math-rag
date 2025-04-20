from openai import AsyncOpenAI

from .openai_batch_managed_llm import OpenAIBatchManagedLLM
from .openai_concurrent_managed_llm import OpenAIConcurrentManagedLLM
from .openai_managed_llm import OpenAIManagedLLM


class OpenAIUnifiedManagedLLM(
    OpenAIManagedLLM, OpenAIBatchManagedLLM, OpenAIConcurrentManagedLLM
):
    def __init__(self, client: AsyncOpenAI):
        OpenAIManagedLLM.__init__(self, client)
        OpenAIBatchManagedLLM.__init__(self, client)
        OpenAIConcurrentManagedLLM.__init__(self, client)
