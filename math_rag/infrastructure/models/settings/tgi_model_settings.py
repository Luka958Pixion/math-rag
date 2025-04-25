from pydantic import RootModel

from .tgi_settings import TGISettings


class TGIModelSettings(RootModel[dict[str, TGISettings]]):
    def __getitem__(self, key: str) -> TGISettings:
        return self.root[key]

    def get(self, key: str, default: TGISettings | None = None) -> TGISettings | None:
        return self.root.get(key, default)

    def keys(self):
        return self.root.keys()

    def values(self):
        return self.root.values()

    def items(self):
        return self.root.items()
