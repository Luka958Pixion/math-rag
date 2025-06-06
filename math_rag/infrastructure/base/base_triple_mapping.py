from abc import ABC, abstractmethod
from typing import Generic, TypeVar


SourceType = TypeVar('SourceType')
TargetType = TypeVar('TargetType')
TargetTypeA = TypeVar('TargetTypeA', bound=TargetType)
TargetTypeB = TypeVar('TargetTypeB', bound=TargetType)
TargetTypeC = TypeVar('TargetTypeC', bound=TargetType)


class BaseTripleMapping(ABC, Generic[SourceType, TargetTypeA, TargetTypeB, TargetTypeC]):
    @classmethod
    @abstractmethod
    def to_source(cls, target: TargetTypeA | TargetTypeB | TargetTypeC, **kwargs) -> SourceType:
        pass

    @classmethod
    @abstractmethod
    def to_target(cls, source: SourceType, **kwargs) -> TargetTypeA | TargetTypeB | TargetTypeC:
        pass
