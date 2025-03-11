from typing import TypeVar

from math_rag.infrastructure.base import BaseMapping

from ...application.types.repositories.source_type import SourceType
from .target_type import TargetType


MappingType = TypeVar('MappingType', bound=BaseMapping[SourceType, TargetType])
