from datetime import datetime
from uuid import UUID, uuid4

from pydantic import Field

from math_rag.infrastructure.base import BaseDocument


class ObjectMetadataDocument(BaseDocument):
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.now)
    object_name: str
    metadata: dict[str, str]
