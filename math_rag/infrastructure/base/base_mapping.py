from abc import ABC, abstractmethod
from typing import Generic

from math_rag.infrastructure.types import SourceType, TargetType


class BaseMapping(ABC, Generic[SourceType, TargetType]):
    @classmethod
    @abstractmethod
    def to_source(cls, target: TargetType) -> SourceType:
        pass

    @classmethod
    @abstractmethod
    def to_target(cls, source: SourceType) -> TargetType:
        pass
