from abc import ABC, abstractmethod
from typing import Generic, TypeVar


SourceType = TypeVar('SourceType')
TargetType = TypeVar('TargetType')
TargetTypeA = TypeVar('TargetTypeA', bound=TargetType)
TargetTypeB = TypeVar('TargetTypeB', bound=TargetType)


class BasePairMapping(ABC, Generic[SourceType, TargetTypeA, TargetTypeB]):
    @classmethod
    @abstractmethod
    def to_source(cls, target: TargetTypeA | TargetTypeB, **kwargs) -> SourceType:
        pass

    @classmethod
    @abstractmethod
    def to_target(cls, source: SourceType, **kwargs) -> TargetTypeA | TargetTypeB:
        pass
