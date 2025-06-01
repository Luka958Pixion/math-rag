from pydantic import RootModel

from .em_model_settings import EMModelSettings


class EMProviderSettings(RootModel[dict[str, EMModelSettings]]):
    def __getitem__(self, key: str) -> EMModelSettings:
        return self.root[key]

    def keys(self):
        return self.root.keys()

    def values(self):
        return self.root.values()

    def items(self):
        return self.root.items()
