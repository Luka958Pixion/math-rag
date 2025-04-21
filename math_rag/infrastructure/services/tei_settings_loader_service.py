from pathlib import Path

from math_rag.infrastructure.models.settings import TEIModelSettings, TEISettings
from math_rag.shared.utils import PydanticOverriderUtil, YamlLoaderUtil


YAML_PATH = Path(__file__).parents[3] / 'settings' / 'text_embeddings_inference.yaml'
DEFAULT = 'default'


class TEISettingsLoaderService:
    def __init__(self):
        self._model_settings = YamlLoaderUtil.load(YAML_PATH, model=TEIModelSettings)

    def load(self, model: str) -> TEISettings:
        default_settings = self._model_settings[DEFAULT]
        override_settings = self._model_settings[model]

        return PydanticOverriderUtil.override(default_settings, override_settings)
