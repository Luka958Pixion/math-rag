from typing import Generic
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.application.types import AssistantInputType


class AssistantRequest(BaseModel, Generic[AssistantInputType]):
    id: UUID = Field(default_factory=uuid4)
    content: AssistantInputType
