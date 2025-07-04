from openai import AsyncOpenAI

from .openai_basic_mm import OpenAIBasicMM


class OpenAIMM(OpenAIBasicMM):
    def __init__(self, client: AsyncOpenAI):
        OpenAIBasicMM.__init__(self, client)
