from abc import ABC, abstractmethod

from math_rag.application.models import (
    BatchEMSettings,
    ConcurrentEMSettings,
    EMSettings,
)


class BaseEMSettingsLoaderService(ABC):
    @abstractmethod
    def load_settings(self) -> EMSettings:
        pass

    @abstractmethod
    def load_batch_settings(self) -> BatchEMSettings:
        pass

    @abstractmethod
    def load_concurrent_settings(self, model: str) -> ConcurrentEMSettings:
        pass
