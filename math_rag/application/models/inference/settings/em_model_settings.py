from pydantic import RootModel

from .em_settings import EMSettings


class EMModelSettings(RootModel[dict[str, EMSettings]]):
    def __getitem__(self, key: str) -> EMSettings:
        return self.root[key]

    def get(self, key: str) -> EMSettings | None:
        return self.root.get(key)

    def keys(self):
        return self.root.keys()

    def values(self):
        return self.root.values()

    def items(self):
        return self.root.items()
