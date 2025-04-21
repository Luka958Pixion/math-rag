from openai import AsyncOpenAI

from .openai_basic_managed_llm import OpenAIBasicManagedLLM
from .openai_batch_managed_llm import OpenAIBatchManagedLLM
from .openai_concurrent_managed_llm import OpenAIConcurrentManagedLLM


class OpenAIManagedLLM(
    OpenAIBasicManagedLLM, OpenAIBatchManagedLLM, OpenAIConcurrentManagedLLM
):
    def __init__(self, client: AsyncOpenAI):
        OpenAIBasicManagedLLM.__init__(self, client)
        OpenAIBatchManagedLLM.__init__(self, client)
        OpenAIConcurrentManagedLLM.__init__(self, client)
