from pathlib import Path

from math_rag.infrastructure.models.settings import TGISettings
from math_rag.shared.utils import YamlLoaderUtil


YAML_PATH = Path(__file__).parents[3] / 'settings' / 'text_generation_inference.yaml'
DEFAULT = 'default'


# TODO by model
class TGISettingsLoaderService:
    def load(self, model: str) -> TGISettings:
        # TODO map / and other special character from hf names
        return YamlLoaderUtil.load(YAML_PATH, model=TGISettings)
