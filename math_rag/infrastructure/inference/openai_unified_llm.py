from openai import AsyncOpenAI

from .openai_batch_llm import OpenAIBatchLLM
from .openai_concurrent_llm import OpenAIConcurrentLLM
from .openai_llm import OpenAILLM


class OpenAIUnifiedLLM(OpenAILLM, OpenAIBatchLLM, OpenAIConcurrentLLM):
    def __init__(self, client: AsyncOpenAI):
        self.client = client
