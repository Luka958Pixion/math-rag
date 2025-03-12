from decouple import config

from math_rag.application.base.services import BaseSettingsLoaderService
from math_rag.application.models import (
    BatchLLMSettings,
    ConcurrentLLMSettings,
    LLMSettings,
)


class SettingsLoaderService(BaseSettingsLoaderService):
    def __init__(self):
        self.llm_settings = LLMSettings(
            max_time=config('max_time', cast=float),
            max_num_retries=config('max_num_retries', cast=int),
        )
        self.batch_llm_settings = BatchLLMSettings(
            poll_interval=config('poll_interval', cast=float),
            max_num_retries=config('max_num_retries', cast=int),
        )
        self.concurrent_llm_settings = ConcurrentLLMSettings(
            max_requests_per_minute=config('max_requests_per_minute', cast=float),
            max_tokens_per_minute=config('max_tokens_per_minute', cast=float),
            max_num_retries=config('max_num_retries', cast=int),
        )

    def load_llm_settings(self) -> LLMSettings:
        return self.llm_settings

    def load_batch_llm_settings(self) -> BatchLLMSettings:
        return self.batch_llm_settings

    def load_concurrent_llm_settings(self) -> ConcurrentLLMSettings:
        return self.concurrent_llm_settings
