from openai import AsyncOpenAI

from .openai_basic_mm import OpenAIBasicMM
from .openai_concurrent_mm import OpenAIConcurrentMM


class OpenAIMM(OpenAIBasicMM, OpenAIConcurrentMM):
    def __init__(self, client: AsyncOpenAI):
        OpenAIBasicMM.__init__(self, client)
        OpenAIConcurrentMM.__init__(self, client)
