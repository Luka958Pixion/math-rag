from pathlib import Path

from math_rag.application.base.services import BaseEMSettingsLoaderService
from math_rag.application.models.settings import (
    BasicEMSettings,
    BatchEMSettings,
    ConcurrentEMSettings,
)
from math_rag.shared.utils import YamlLoaderUtil


YAML_PATH = Path(__file__).parents[3] / 'settings' / 'embedding_models.yaml'


class EMSettingsLoaderService(BaseEMSettingsLoaderService):
    def load_basic_settings(self) -> BasicEMSettings:
        return YamlLoaderUtil.load(YAML_PATH, model=...)  # TODO

    def load_batch_settings(self) -> BatchEMSettings:
        return YamlLoaderUtil.load(YAML_PATH, model=...)

    def load_concurrent_settings(self) -> ConcurrentEMSettings:
        return YamlLoaderUtil.load(YAML_PATH, model=...)
