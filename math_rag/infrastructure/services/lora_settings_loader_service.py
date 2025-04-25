from pathlib import Path

from math_rag.infrastructure.models.settings import LoRAModelSettings, LoRASettings
from math_rag.shared.utils import PydanticOverriderUtil, YamlLoaderUtil


YAML_PATH = Path(__file__).parents[3] / 'settings' / 'low_rank_adaptation.yaml'
DEFAULT = 'default'


class LoRASettingsLoaderService:
    def __init__(self):
        self._model_settings = YamlLoaderUtil.load(YAML_PATH, model=LoRAModelSettings)

    def load(self, model: str) -> LoRASettings:
        default_settings = self._model_settings[DEFAULT]
        override_settings = self._model_settings.get(model, None)

        if not override_settings:
            return default_settings

        return PydanticOverriderUtil.override(default_settings, override_settings)
