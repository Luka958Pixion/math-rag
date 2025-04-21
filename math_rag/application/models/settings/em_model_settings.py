from pydantic import BaseModel

from .em_settings import EMSettings


class EMModelSettings(BaseModel):
    __root__: dict[str, EMSettings]

    def __getitem__(self, key: str) -> EMSettings:
        return self.__root__[key]

    def keys(self):
        return self.__root__.keys()

    def values(self):
        return self.__root__.values()

    def items(self):
        return self.__root__.items()
