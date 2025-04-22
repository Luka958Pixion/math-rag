from pydantic import RootModel

from .lora_settings import LoRASettings


class LoRAModelSettings(RootModel[dict[str, LoRASettings]]):
    def __getitem__(self, key: str) -> LoRASettings:
        return self.root[key]

    def keys(self):
        return self.root.keys()

    def values(self):
        return self.root.values()

    def items(self):
        return self.root.items()
