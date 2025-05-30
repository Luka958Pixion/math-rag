from abc import ABC
from datetime import datetime
from typing import Generic
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.core.enums import DatasetBuildStatus
from math_rag.core.types import DatasetBuildStageType, SampleType

from .base_dataset_build_stage import BaseDatasetBuildStage


class BaseDataset(BaseModel, Generic[SampleType, DatasetBuildStageType], ABC):
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.now)
    build_stage: DatasetBuildStageType
    build_status: DatasetBuildStatus
    build_from_dataset_id: UUID | None = None
    build_from_stage: BaseDatasetBuildStage | None = None
    samples: list[SampleType] = Field(default_factory=list)
