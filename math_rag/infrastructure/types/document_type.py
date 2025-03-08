from typing import TYPE_CHECKING, TypeVar


if TYPE_CHECKING:
    from math_rag.infrastructure.base import BaseDocument

DocumentType = TypeVar('DocumentType', bound=BaseDocument)
