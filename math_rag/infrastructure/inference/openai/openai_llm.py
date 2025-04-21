from openai import AsyncOpenAI

from .openai_basic_llm import OpenAIBasicLLM
from .openai_batch_llm import OpenAIBatchLLM
from .openai_concurrent_llm import OpenAIConcurrentLLM


class OpenAILLM(OpenAIBasicLLM, OpenAIBatchLLM, OpenAIConcurrentLLM):
    def __init__(self, client: AsyncOpenAI):
        OpenAIBasicLLM.__init__(self, client)
        OpenAIBatchLLM.__init__(self, client)
        OpenAIConcurrentLLM.__init__(self, client)
