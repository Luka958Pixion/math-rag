from typing import TypeVar

from math_rag.infrastructure.base import BaseTripleMapping

from .source_type import SourceType
from .target_type import TargetType


TargetTypeA = TypeVar('TargetTypeA', bound=TargetType)
TargetTypeB = TypeVar('TargetTypeB', bound=TargetType)
TargetTypeC = TypeVar('TargetTypeC', bound=TargetType)

TripleMappingType = TypeVar(
    'TripleMappingType', bound=BaseTripleMapping[SourceType, TargetTypeA, TargetTypeB, TargetTypeC]
)
