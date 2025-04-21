from pathlib import Path

from math_rag.application.base.services import BaseEMSettingsLoaderService
from math_rag.application.constants import DEFAULT_MODEL, DEFAULT_PROVIDER
from math_rag.application.models.settings import (
    BasicEMSettings,
    BatchEMSettings,
    ConcurrentEMSettings,
    EMProviderSettings,
)
from math_rag.shared.utils import PydanticOverriderUtil, YamlLoaderUtil


YAML_PATH = Path(__file__).parents[3] / 'settings' / 'embedding_models.yaml'


class EMSettingsLoaderService(BaseEMSettingsLoaderService):
    def __init__(self):
        self._provider_settings = YamlLoaderUtil.load(
            YAML_PATH, model=EMProviderSettings
        )
        self._default_settings = self._provider_settings[DEFAULT_PROVIDER][
            DEFAULT_MODEL
        ]

    def load_basic_settings(self, provider: str, model: str) -> BasicEMSettings:
        if provider == DEFAULT_PROVIDER:
            return self._default_settings.basic_settings

        return PydanticOverriderUtil.override_non_none_fields(
            self._default_settings.basic_settings,
            self._provider_settings[provider][model].basic_settings,
        )

    def load_batch_settings(self, provider: str, model: str) -> BatchEMSettings:
        if provider == DEFAULT_PROVIDER:
            return self._default_settings.batch_settings

        return PydanticOverriderUtil.override_non_none_fields(
            self._default_settings.batch_settings,
            self._provider_settings[provider][model].batch_settings,
        )

    def load_concurrent_settings(
        self, provider: str, model: str
    ) -> ConcurrentEMSettings:
        if provider == DEFAULT_PROVIDER:
            return self._default_settings.concurrent_settings

        return PydanticOverriderUtil.override_non_none_fields(
            self._default_settings.concurrent_settings,
            self._provider_settings[provider][model].concurrent_settings,
        )
