from pathlib import Path

from pydantic import RootModel

from math_rag.infrastructure.models.hpc.pbs import PBSProResourceList
from math_rag.shared.utils import PydanticOverriderUtil, YamlReaderUtil


YAML_PATH = Path(__file__).parents[3] / 'settings' / 'inference' / 'text_generation_inference.yaml'
DEFAULT = 'default'


class _PBSProResourceListMapping(RootModel[dict[str, PBSProResourceList]]):
    def __getitem__(self, key: str) -> PBSProResourceList:
        return self.root[key]

    def get(self, key: str, default: PBSProResourceList | None = None) -> PBSProResourceList | None:
        return self.root.get(key, default)

    def keys(self):
        return self.root.keys()

    def values(self):
        return self.root.values()

    def items(self):
        return self.root.items()


class PBSProResourceListLoaderService:
    def __init__(self):
        self._model_settings = YamlReaderUtil.read(YAML_PATH, model=_PBSProResourceListMapping)

    def load(self, model: str) -> PBSProResourceList:
        default_settings = self._model_settings[DEFAULT]
        override_settings = self._model_settings.get(model, None)

        if not override_settings:
            return default_settings

        return PydanticOverriderUtil.override(default_settings, override_settings)
