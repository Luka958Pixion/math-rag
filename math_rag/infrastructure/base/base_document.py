from abc import ABC, abstractmethod
from typing import Generic

from pydantic import BaseModel

from math_rag.infrastructure.types import DocumentType, InternalType


class BaseDocument(BaseModel, ABC, Generic[DocumentType, InternalType]):
    @classmethod
    @abstractmethod
    def from_internal(cls: type[DocumentType], inter: InternalType) -> DocumentType:
        pass

    @classmethod
    @abstractmethod
    def to_internal(cls: type[InternalType], doc: DocumentType) -> InternalType:
        pass
