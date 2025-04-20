from decouple import config

from math_rag.application.base.services import BaseSettingsLoaderService
from math_rag.application.models import (
    BatchEMSettings,
    BatchLLMSettings,
    ConcurrentEMSettings,
    ConcurrentLLMSettings,
    EMSettings,
    LLMSettings,
)


class SettingsLoaderService(BaseSettingsLoaderService):
    def __init__(self):
        self._llm_settings = LLMSettings(
            max_time=config('LLM_MAX_TIME', cast=float),
            max_num_retries=config('LLM_MAX_NUM_RETRIES', cast=int),
        )
        self._batch_llm_settings = BatchLLMSettings(
            poll_interval=config('BATCH_LLM_POLL_INTERVAL', cast=float),
            max_num_retries=config('BATCH_LLM_MAX_NUM_RETRIES', cast=int),
        )
        self._concurrent_llm_settings = ConcurrentLLMSettings(
            max_requests_per_minute=config(
                'CONCURRENT_LLM_MAX_REQUESTS_PER_MINUTE', cast=float
            ),
            max_tokens_per_minute=config(
                'CONCURRENT_LLM_MAX_TOKENS_PER_MINUTE', cast=float
            ),
            max_num_retries=config('CONCURRENT_LLM_MAX_NUM_RETRIES', cast=int),
        )
        self._em_settings = EMSettings(
            max_time=config('EM_MAX_TIME', cast=float),
            max_num_retries=config('EM_MAX_NUM_RETRIES', cast=int),
        )
        self._batch_em_settings = BatchEMSettings(
            poll_interval=config('BATCH_EM_POLL_INTERVAL', cast=float),
            max_num_retries=config('BATCH_EM_MAX_NUM_RETRIES', cast=int),
        )
        self._concurrent_em_settings = ConcurrentEMSettings(
            max_requests_per_minute=config(
                'CONCURRENT_EM_MAX_REQUESTS_PER_MINUTE', cast=float
            ),
            max_tokens_per_minute=config(
                'CONCURRENT_EM_MAX_TOKENS_PER_MINUTE', cast=float
            ),
            max_num_retries=config('CONCURRENT_EM_MAX_NUM_RETRIES', cast=int),
        )

    def load_llm_settings(self) -> LLMSettings:
        return self._llm_settings

    def load_batch_llm_settings(self) -> BatchLLMSettings:
        return self._batch_llm_settings

    def load_concurrent_llm_settings(self) -> ConcurrentLLMSettings:
        return self._concurrent_llm_settings

    def load_em_settings(self) -> EMSettings:
        return self._em_settings

    def load_batch_llm_settings(self) -> BatchEMSettings:
        return self._batch_em_settings

    def load_concurrent_llm_settings(self) -> ConcurrentEMSettings:
        return self._concurrent_em_settings
