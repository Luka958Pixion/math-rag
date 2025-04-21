from pathlib import Path

from math_rag.application.base.services import BaseLLMSettingsLoaderService
from math_rag.application.models.settings import (
    BatchLLMSettings,
    ConcurrentLLMSettings,
    LLMSettings,
)
from math_rag.shared.utils import YamlLoaderUtil


YAML_PATH = Path(__file__).parents[3] / 'settings' / 'large_language_models.yaml'


class LLMSettingsLoaderService(BaseLLMSettingsLoaderService):
    def load_settings(self) -> LLMSettings:
        return YamlLoaderUtil.load(YAML_PATH, model=...)  # TODO

    def load_batch_settings(self) -> BatchLLMSettings:
        return YamlLoaderUtil.load(YAML_PATH, model=...)

    def load_concurrent_settings(self) -> ConcurrentLLMSettings:
        return YamlLoaderUtil.load(YAML_PATH, model=...)
