from pathlib import Path

from math_rag.application.models.fine_tune.settings import FineTuneSettings
from math_rag.shared.utils import YamlLoaderUtil


BASE_PATH = Path(__file__).parents[3] / 'settings' / 'fine_tune'


class FineTuneSettingsLoaderService:
    def load(self, provider_name: str, model_name: str) -> FineTuneSettings:
        path = BASE_PATH / provider_name / f'{model_name}.yaml'

        return YamlLoaderUtil.load(path, model=FineTuneSettings)
