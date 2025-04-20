from abc import ABC, abstractmethod

from math_rag.application.models import (
    BatchEMSettings,
    BatchLLMSettings,
    ConcurrentEMSettings,
    ConcurrentLLMSettings,
    EMSettings,
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

    @abstractmethod
    def load_em_settings(self) -> EMSettings:
        pass

    @abstractmethod
    def load_batch_em_settings(self) -> BatchEMSettings:
        pass

    @abstractmethod
    def load_concurrent_em_settings(self) -> ConcurrentEMSettings:
        pass
