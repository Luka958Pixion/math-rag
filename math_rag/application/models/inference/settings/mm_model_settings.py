from pydantic import RootModel

from .mm_settings import MMSettings


class MMModelSettings(RootModel[dict[str, MMSettings]]):
    def __getitem__(self, key: str) -> MMSettings:
        return self.root[key]

    def get(self, key: str) -> MMSettings | None:
        return self.root.get(key)

    def keys(self):
        return self.root.keys()

    def values(self):
        return self.root.values()

    def items(self):
        return self.root.items()
