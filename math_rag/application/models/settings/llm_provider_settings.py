from pydantic import RootModel

from .llm_model_settings import LLMModelSettings


class LLMProviderSettings(RootModel[dict[str, LLMModelSettings]]):
    def __getitem__(self, key: str) -> LLMModelSettings:
        return self.root[key]

    def keys(self):
        return self.root.keys()

    def values(self):
        return self.root.values()

    def items(self):
        return self.root.items()
