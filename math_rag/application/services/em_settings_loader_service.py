from pathlib import Path

from math_rag.application.base.services import BaseEMSettingsLoaderService
from math_rag.application.models.inference.settings import (
    BasicEMSettings,
    BatchEMSettings,
    ConcurrentEMSettings,
    EMProviderSettings,
)
from math_rag.shared.utils import PydanticOverriderUtil, YamlLoaderUtil


YAML_PATH = Path(__file__).parents[3] / 'settings' / 'embedding_models.yaml'
DEFAULT = 'default'


class EMSettingsLoaderService(BaseEMSettingsLoaderService):
    def __init__(self):
        self._provider_settings = YamlLoaderUtil.load(YAML_PATH, model=EMProviderSettings)
        self._default_settings = self._provider_settings[DEFAULT][DEFAULT]

    def load_basic_settings(self, provider: str, model: str) -> BasicEMSettings:
        default_basic_settings = self._default_settings.basic
        override_basic_settings = self._provider_settings[provider][model].basic

        if default_basic_settings is None:
            raise ValueError('Default basic settings must not be None')

        if provider == DEFAULT or override_basic_settings is None:
            return default_basic_settings

        return PydanticOverriderUtil.override(
            default_basic_settings,
            override_basic_settings,
        )

    def load_batch_settings(self, provider: str, model: str) -> BatchEMSettings:
        default_batch_settings = self._default_settings.batch
        override_batch_settings = self._provider_settings[provider][model].batch

        if default_batch_settings is None:
            raise ValueError('Default batch settings must not be None')

        if provider == DEFAULT or override_batch_settings is None:
            return default_batch_settings

        return PydanticOverriderUtil.override(
            default_batch_settings,
            override_batch_settings,
        )

    def load_concurrent_settings(self, provider: str, model: str) -> ConcurrentEMSettings:
        default_concurrent_settings = self._default_settings.concurrent
        override_concurrent_settings = self._provider_settings[provider][model].concurrent

        if default_concurrent_settings is None:
            raise ValueError('Default concurrent settings must not be None')

        if provider == DEFAULT or override_concurrent_settings is None:
            return default_concurrent_settings

        return PydanticOverriderUtil.override(
            default_concurrent_settings,
            override_concurrent_settings,
        )
