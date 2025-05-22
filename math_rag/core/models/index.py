from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.core.enums import IndexBuildStage, IndexBuildStatus


class Index(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.now)
    build_stage: IndexBuildStage = Field(default=IndexBuildStage.LOADING_MATH_ARTICLES)
    build_status: IndexBuildStatus = Field(default=IndexBuildStatus.PENDING)
    build_from_index_id: UUID | None = None
    build_from_stage: IndexBuildStage | None = None
