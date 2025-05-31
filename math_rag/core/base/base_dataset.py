from abc import ABC
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.core.enums import DatasetBuildStatus


class BaseDataset(BaseModel, ABC):
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.now)
    build_status: DatasetBuildStatus = Field(default=DatasetBuildStatus.PENDING)
    build_from_dataset_id: UUID | None = None
