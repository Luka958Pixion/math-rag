from math_rag.application.models import (
    BatchLLMSettings,
    ConcurrentLLMSettings,
    LLMSettings,
)


class SettingsLoaderService:
    def load_llm_settings(self) -> LLMSettings:
        pass

    def load_batch_llm_settings(self) -> BatchLLMSettings:
        pass

    def load_concurrent_llm_settings(self) -> ConcurrentLLMSettings:
        pass
