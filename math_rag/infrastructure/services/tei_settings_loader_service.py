from pathlib import Path

from math_rag.infrastructure.models.settings import TEISettings
from math_rag.shared.utils import YamlLoaderUtil


YAML_PATH = Path(__file__).parents[3] / 'settings' / 'text_embeddings_inference.yaml'
DEFAULT = 'default'


# TODO by model
class TEISettingsLoaderService:
    def load(self, model: str) -> TEISettings:
        return YamlLoaderUtil.load(YAML_PATH, model=TEISettings)
