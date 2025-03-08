from abc import ABC, abstractmethod

from pydantic import BaseModel


class BaseDocument(BaseModel, ABC):
    @classmethod
    @abstractmethod
    def from_internal(cls, inter: BaseModel) -> 'BaseDocument':
        pass

    @classmethod
    @abstractmethod
    def to_internal(cls, doc: 'BaseDocument') -> BaseModel:
        pass
