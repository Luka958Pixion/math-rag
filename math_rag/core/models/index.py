from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.core.enums import IndexBuildStage


class Index(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=datetime.now)
    build_stage: IndexBuildStage = Field(default=IndexBuildStage.LOAD_MATH_ARTICLES)
