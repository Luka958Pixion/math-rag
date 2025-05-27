from typing import TypeVar

from math_rag.infrastructure.base import BaseDocumentView


TargetType = TypeVar('TargetType', bound=BaseDocumentView)
