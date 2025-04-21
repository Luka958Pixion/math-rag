from decouple import config

from math_rag.application.base.services import BaseLLMSettingsLoaderService
from math_rag.application.models import (
    BatchLLMSettings,
    ConcurrentLLMSettings,
    LLMSettings,
)


class LLMSettingsLoaderService(BaseLLMSettingsLoaderService):
    def __init__(self):
        self._settings = LLMSettings(
            max_time=config('LLM_MAX_TIME', cast=float),
            max_num_retries=config('LLM_MAX_NUM_RETRIES', cast=int),
        )
        self._batch_settings = BatchLLMSettings(
            poll_interval=config('BATCH_LLM_POLL_INTERVAL', cast=float),
            max_num_retries=config('BATCH_LLM_MAX_NUM_RETRIES', cast=int),
        )
        self._concurrent_settings = ConcurrentLLMSettings(
            max_requests_per_minute=config(
                'CONCURRENT_LLM_MAX_REQUESTS_PER_MINUTE',
                cast=float,  # TODO
            ),
            max_tokens_per_minute=config(
                'CONCURRENT_LLM_MAX_TOKENS_PER_MINUTE',
                cast=float,  # TODO
            ),
            max_num_retries=config('CONCURRENT_LLM_MAX_NUM_RETRIES', cast=int),
        )

    def load_settings(self) -> LLMSettings:
        return self._settings

    def load_batch_settings(self) -> BatchLLMSettings:
        return self._batch_settings

    def load_concurrent_settings(self) -> ConcurrentLLMSettings:
        return self._concurrent_settings
