from abc import ABC, abstractmethod

from math_rag.application.models import (
    BatchLLMSettings,
    ConcurrentLLMSettings,
    LLMSettings,
)


class BaseLLMSettingsLoaderService(ABC):
    @abstractmethod
    def load_settings(self) -> LLMSettings:
        pass

    @abstractmethod
    def load_batch_settings(self) -> BatchLLMSettings:
        pass

    @abstractmethod
    def load_concurrent_settings(self) -> ConcurrentLLMSettings:
        pass
