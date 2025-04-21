from pydantic import BaseModel

from .em_model_settings import EMModelSettings


class EMProviderSettings(BaseModel):
    __root__: dict[str, EMModelSettings]

    def __getitem__(self, key: str) -> EMModelSettings:
        return self.__root__[key]

    def keys(self):
        return self.__root__.keys()

    def values(self):
        return self.__root__.values()

    def items(self):
        return self.__root__.items()
