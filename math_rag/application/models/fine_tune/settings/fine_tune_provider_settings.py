from pydantic import RootModel

from .fine_tune_settings import FineTuneSettings


class FineTuneProviderSettings(RootModel[dict[str, FineTuneSettings]]):
    def __getitem__(self, key: str) -> FineTuneSettings:
        return self.root[key]

    def keys(self):
        return self.root.keys()

    def values(self):
        return self.root.values()

    def items(self):
        return self.root.items()
