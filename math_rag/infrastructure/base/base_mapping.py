from abc import ABC, abstractmethod
from typing import Generic, TypeVar


SourceType = TypeVar('SourceType')
TargetType = TypeVar('TargetType')


class BaseMapping(ABC, Generic[SourceType, TargetType]):
    @staticmethod
    @abstractmethod
    def to_source(target: TargetType, **kwargs) -> SourceType:
        pass

    @staticmethod
    @abstractmethod
    def to_target(source: SourceType, **kwargs) -> TargetType:
        pass
