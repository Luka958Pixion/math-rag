from pathlib import Path
from typing import Literal

from pydantic import RootModel

from math_rag.infrastructure.models.hpc.pbs import PBSProResourceList
from math_rag.shared.utils import PydanticOverriderUtil, YamlReaderUtil


RESOURCES_PATH = Path(__file__).parents[3] / 'settings' / 'resources'
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
        self._model_settings_dict = {
            'ft': YamlReaderUtil.read(
                RESOURCES_PATH / 'fine_tune.yaml', model=_PBSProResourceListMapping
            ),
            'tgi': YamlReaderUtil.read(
                RESOURCES_PATH / 'text_embeddings_inference.yaml', model=_PBSProResourceListMapping
            ),
            'tei': YamlReaderUtil.read(
                'text_generation_inference.yaml', model=_PBSProResourceListMapping
            ),
        }

    def load(self, model: str, *, use_case: Literal['ft', 'tgi', 'tei']) -> PBSProResourceList:
        model_settings = self._model_settings_dict[use_case]
        default_settings = model_settings[DEFAULT]
        override_settings = model_settings.get(model, None)

        if not override_settings:
            return default_settings

        return PydanticOverriderUtil.override(default_settings, override_settings)
