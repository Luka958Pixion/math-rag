from abc import ABC, abstractmethod

from math_rag.infrastructure.models.settings import (
    BasicEMSettings,
    BatchEMSettings,
    ConcurrentEMSettings,
)


class BaseEMSettingsLoaderService(ABC):
    @abstractmethod
    def load_basic_settings(self) -> BasicEMSettings:
        pass

    @abstractmethod
    def load_batch_settings(self) -> BatchEMSettings:
        pass

    @abstractmethod
    def load_concurrent_settings(self, model: str) -> ConcurrentEMSettings:
        pass
