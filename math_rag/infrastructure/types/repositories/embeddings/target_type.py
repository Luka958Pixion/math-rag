from typing import TypeVar

from math_rag.infrastructure.base import BaseEmbedding


TargetType = TypeVar('TargetType', bound=BaseEmbedding)
