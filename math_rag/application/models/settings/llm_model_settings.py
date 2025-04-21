from pydantic import BaseModel

from .llm_settings import LLMSettings


class LLMModelSettings(BaseModel):
    __root__: dict[str, LLMSettings]

    def __getitem__(self, key: str) -> LLMSettings:
        return self.__root__[key]

    def keys(self):
        return self.__root__.keys()

    def values(self):
        return self.__root__.values()

    def items(self):
        return self.__root__.items()
