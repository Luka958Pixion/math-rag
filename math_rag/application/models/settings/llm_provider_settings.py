from pydantic import BaseModel

from .llm_model_settings import LLMModelSettings


class LLMProviderSettings(BaseModel):
    __root__: dict[str, LLMModelSettings]

    def __getitem__(self, key: str) -> LLMModelSettings:
        return self.__root__[key]

    def keys(self):
        return self.__root__.keys()

    def values(self):
        return self.__root__.values()

    def items(self):
        return self.__root__.items()
