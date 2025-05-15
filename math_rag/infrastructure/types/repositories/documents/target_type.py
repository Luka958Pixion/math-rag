from typing import TypeVar

from math_rag.infrastructure.base import BaseDocument


TargetType = TypeVar('TargetType', bound=BaseDocument)
