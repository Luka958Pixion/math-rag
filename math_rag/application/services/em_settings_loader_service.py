from pathlib import Path
from typing import Callable, TypeVar

from math_rag.application.base.services import BaseEMSettingsLoaderService
from math_rag.application.models.inference.settings import (
    BasicEMSettings,
    BatchEMSettings,
    ConcurrentEMSettings,
    EMProviderSettings,
    EMSettings,
)
from math_rag.shared.utils import PydanticOverriderUtil, YamlReaderUtil


T = TypeVar('T')

YAML_PATH = Path(__file__).parents[3] / 'settings' / 'inference' / 'embedding_models.yaml'
DEFAULT = 'default'


class EMSettingsLoaderService(BaseEMSettingsLoaderService):
    def __init__(self):
        self._provider_settings = YamlReaderUtil.read(YAML_PATH, model=EMProviderSettings)
        self._default_settings = self._provider_settings[DEFAULT][DEFAULT]

    def _load_settings(
        self,
        provider: str,
        model: str,
        settings_getter: Callable[[EMSettings], T | None],
        settings_type: type[T],
    ) -> T:
        default = settings_getter(self._default_settings)
        if default is None:
            raise ValueError(f'Default {settings_type.__name__} settings must not be None')

        provider_dict = self._provider_settings.get(provider)
        if provider_dict is None:
            return default

        model_settings = provider_dict.get(model)
        if model_settings is None:
            return default

        override = settings_getter(model_settings)
        if override is None:
            return default

        return PydanticOverriderUtil.override(default, override)

    def load_basic_settings(self, provider: str, model: str) -> BasicEMSettings:
        return self._load_settings(
            provider,
            model,
            lambda x: x.basic,
            BasicEMSettings,
        )

    def load_batch_settings(self, provider: str, model: str) -> BatchEMSettings:
        return self._load_settings(
            provider,
            model,
            lambda x: x.batch,
            BatchEMSettings,
        )

    def load_concurrent_settings(self, provider: str, model: str) -> ConcurrentEMSettings:
        return self._load_settings(
            provider,
            model,
            lambda x: x.concurrent,
            ConcurrentEMSettings,
        )
