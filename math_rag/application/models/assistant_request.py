from typing import Generic
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.application.types import AssistantRequestType


class AssistantRequest(BaseModel, Generic[AssistantRequestType]):
    id: UUID = Field(default_factory=uuid4)
    content: AssistantRequestType
