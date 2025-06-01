from abc import ABC, abstractmethod

from math_rag.application.models.inference.settings import (
    BasicLLMSettings,
    BatchLLMSettings,
    ConcurrentLLMSettings,
)


class BaseLLMSettingsLoaderService(ABC):
    @abstractmethod
    def load_basic_settings(self, provider: str, model: str) -> BasicLLMSettings:
        pass

    @abstractmethod
    def load_batch_settings(self, provider: str, model: str) -> BatchLLMSettings:
        pass

    @abstractmethod
    def load_concurrent_settings(self, provider: str, model: str) -> ConcurrentLLMSettings:
        pass
