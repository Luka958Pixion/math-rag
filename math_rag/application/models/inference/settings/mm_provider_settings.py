from pydantic import RootModel

from .mm_model_settings import MMModelSettings


class MMProviderSettings(RootModel[dict[str, MMModelSettings]]):
    def __getitem__(self, key: str) -> MMModelSettings:
        return self.root[key]

    def get(self, key: str) -> MMModelSettings | None:
        return self.root.get(key)

    def keys(self):
        return self.root.keys()

    def values(self):
        return self.root.values()

    def items(self):
        return self.root.items()
