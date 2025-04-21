from pathlib import Path

from math_rag.application.base.services import BaseLLMSettingsLoaderService
from math_rag.application.models.settings import (
    BasicLLMSettings,
    BatchLLMSettings,
    ConcurrentLLMSettings,
    LLMModelSettings,
    LLMProviderSettings,
)
from math_rag.shared.utils import PydanticOverriderUtil, YamlLoaderUtil


YAML_PATH = Path(__file__).parents[3] / 'settings' / 'large_language_models.yaml'
DEFAULT_PROVIDER = 'default'


class LLMSettingsLoaderService(BaseLLMSettingsLoaderService):
    def __init__(self):
        self._provider_settings = YamlLoaderUtil.load(
            YAML_PATH, model=LLMProviderSettings
        )
        self._default_model_settings = self._provider_settings[DEFAULT_PROVIDER]

    def load_basic_settings(self, provider: str, model: str) -> BasicLLMSettings:
        default_basic_settings = self._default_model_settings[model].basic_settings

        if provider == DEFAULT_PROVIDER:
            return default_basic_settings

        override_settings = self._provider_settings[provider][model]
        basic_settings = PydanticOverriderUtil.override_non_none_fields(
            default_basic_settings, override_settings.basic_settings
        )

        return basic_settings

    def load_batch_settings(self, provider: str, model: str) -> BatchLLMSettings:
        pass

    def load_concurrent_settings(
        self, provider: str, model: str
    ) -> ConcurrentLLMSettings:
        pass
