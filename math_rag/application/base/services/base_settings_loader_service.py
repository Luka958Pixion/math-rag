from abc import ABC, abstractmethod

from math_rag.application.models import (
    BatchLLMSettings,
    ConcurrentLLMSettings,
    LLMSettings,
)


class BaseSettingsLoaderService(ABC):
    @abstractmethod
    def load_llm_settings(self) -> LLMSettings:
        pass

    @abstractmethod
    def load_batch_llm_settings(self) -> BatchLLMSettings:
        pass

    @abstractmethod
    def load_concurrent_llm_settings(self) -> ConcurrentLLMSettings:
        pass
