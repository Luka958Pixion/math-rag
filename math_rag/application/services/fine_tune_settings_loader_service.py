from pathlib import Path

from math_rag.application.models.fine_tune.settings import (
    FineTuneProviderSettings,
    FineTuneSettings,
)
from math_rag.shared.utils import YamlLoaderUtil


YAML_PATH = Path(__file__).parents[3] / 'settings' / 'fine_tune' / 'low_rank_adaptation.yaml'
DEFAULT = 'default'


class FineTuneSettingsLoaderService:
    def load(self, name: str) -> FineTuneSettings:
        return YamlLoaderUtil.load(YAML_PATH, model=FineTuneProviderSettings)[name]
