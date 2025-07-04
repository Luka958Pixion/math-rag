from abc import ABC, abstractmethod

from math_rag.application.models.inference.settings import BasicMMSettings


class BaseMMSettingsLoaderService(ABC):
    @abstractmethod
    def load_basic_settings(self, provider: str, model: str) -> BasicMMSettings:
        pass
