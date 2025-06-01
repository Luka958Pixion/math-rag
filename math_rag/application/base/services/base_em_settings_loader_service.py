from abc import ABC, abstractmethod

from math_rag.application.models.inference.settings import (
    BasicEMSettings,
    BatchEMSettings,
    ConcurrentEMSettings,
)


class BaseEMSettingsLoaderService(ABC):
    @abstractmethod
    def load_basic_settings(self, provider: str, model: str) -> BasicEMSettings:
        pass

    @abstractmethod
    def load_batch_settings(self, provider: str, model: str) -> BatchEMSettings:
        pass

    @abstractmethod
    def load_concurrent_settings(self, provider: str, model: str) -> ConcurrentEMSettings:
        pass
