from pydantic import RootModel

from .tgi_settings import TGISettings


class TGIModelSettings(RootModel[dict[str, TGISettings]]):
    def __getitem__(self, key: str) -> TGISettings:
        return self.root[key]

    def keys(self):
        return self.root.keys()

    def values(self):
        return self.root.values()

    def items(self):
        return self.root.items()
