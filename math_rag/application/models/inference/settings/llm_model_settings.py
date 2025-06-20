from pydantic import RootModel

from .llm_settings import LLMSettings


class LLMModelSettings(RootModel[dict[str, LLMSettings]]):
    def __getitem__(self, key: str) -> LLMSettings:
        return self.root[key]

    def get(self, key: str) -> LLMSettings | None:
        return self.root.get(key)

    def keys(self):
        return self.root.keys()

    def values(self):
        return self.root.values()

    def items(self):
        return self.root.items()
