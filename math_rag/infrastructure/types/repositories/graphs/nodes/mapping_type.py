from typing import TypeVar

from math_rag.infrastructure.base import BaseMapping

from .source_types import SourceNodeType, SourceRelType
from .target_types import TargetNodeType, TargetRelType


MappingNodeType = TypeVar('MappingNodeType', bound=BaseMapping[SourceNodeType, TargetNodeType])
MappingRelType = TypeVar('MappingRelType', bound=BaseMapping[SourceRelType, TargetRelType])
