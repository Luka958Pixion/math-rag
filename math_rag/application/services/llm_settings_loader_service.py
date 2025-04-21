from pathlib import Path

from math_rag.application.base.services import BaseLLMSettingsLoaderService
from math_rag.application.models.settings import (
    BasicLLMSettings,
    BatchLLMSettings,
    ConcurrentLLMSettings,
    LLMProviderSettings,
)
from math_rag.shared.utils import PydanticOverriderUtil, YamlLoaderUtil


YAML_PATH = Path(__file__).parents[3] / 'settings' / 'large_language_models.yaml'
DEFAULT = 'default'


class LLMSettingsLoaderService(BaseLLMSettingsLoaderService):
    def __init__(self):
        self._provider_settings = YamlLoaderUtil.load(
            YAML_PATH, model=LLMProviderSettings
        )
        self._default_settings = self._provider_settings[DEFAULT][DEFAULT]

    def load_basic_settings(self, provider: str, model: str) -> BasicLLMSettings:
        if provider == DEFAULT:
            return self._default_settings.basic_settings

        return PydanticOverriderUtil.override_non_none_fields(
            self._default_settings.basic_settings,
            self._provider_settings[provider][model].basic_settings,
        )

    def load_batch_settings(self, provider: str, model: str) -> BatchLLMSettings:
        if provider == DEFAULT:
            return self._default_settings.batch_settings

        return PydanticOverriderUtil.override_non_none_fields(
            self._default_settings.batch_settings,
            self._provider_settings[provider][model].batch_settings,
        )

    def load_concurrent_settings(
        self, provider: str, model: str
    ) -> ConcurrentLLMSettings:
        if provider == DEFAULT:
            return self._default_settings.concurrent_settings

        return PydanticOverriderUtil.override_non_none_fields(
            self._default_settings.concurrent_settings,
            self._provider_settings[provider][model].concurrent_settings,
        )
