from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.core.enums import DatasetBuildStage, DatasetBuildStatus


class Dataset(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.now)
    build_stage: DatasetBuildStage = Field(default=DatasetBuildStage.LOAD_MATH_ARTICLES)
    build_status: DatasetBuildStatus = Field(default=DatasetBuildStatus.PENDING)
    build_from_dataset_id: UUID | None = None
    build_from_stage: DatasetBuildStage | None = None
    math_article_ids: list[UUID] = Field(default_factory=list)
    math_expression_ids: list[UUID] = Field(default_factory=list)
    math_expression_label_ids: list[UUID] = Field(default_factory=list)
