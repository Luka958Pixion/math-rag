from pydantic import RootModel

from .tei_settings import TEISettings


class TEIModelSettings(RootModel[dict[str, TEISettings]]):
    def __getitem__(self, key: str) -> TEISettings:
        return self.root[key]

    def keys(self):
        return self.root.keys()

    def values(self):
        return self.root.values()

    def items(self):
        return self.root.items()
