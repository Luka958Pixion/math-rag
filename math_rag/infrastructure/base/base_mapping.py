from abc import ABC, abstractmethod
from typing import Generic, TypeVar


SourceType = TypeVar('SourceType')
TargetType = TypeVar('TargetType')


class BaseMapping(ABC, Generic[SourceType, TargetType]):
    @classmethod
    @abstractmethod
    def to_source(cls, target: TargetType) -> SourceType:
        pass

    @classmethod
    @abstractmethod
    def to_target(cls, source: SourceType) -> TargetType:
        pass
