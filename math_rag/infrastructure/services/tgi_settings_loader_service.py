from pathlib import Path

from math_rag.infrastructure.models.inference.settings import TGIModelSettings, TGISettings
from math_rag.shared.utils import PydanticOverriderUtil, YamlLoaderUtil


YAML_PATH = Path(__file__).parents[3] / 'settings' / 'inference' / 'text_generation_inference.yaml'
DEFAULT = 'default'


class TGISettingsLoaderService:
    def __init__(self):
        self._model_settings = YamlLoaderUtil.load(YAML_PATH, model=TGIModelSettings)

    def load(self, model: str) -> TGISettings:
        default_settings = self._model_settings[DEFAULT]
        override_settings = self._model_settings.get(model, None)

        if not override_settings:
            return default_settings

        return PydanticOverriderUtil.override(default_settings, override_settings)
