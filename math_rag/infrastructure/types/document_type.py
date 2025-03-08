from typing import TypeVar

from math_rag.infrastructure.base import BaseDocument


DocumentType = TypeVar('DocumentType', bound=BaseDocument)
