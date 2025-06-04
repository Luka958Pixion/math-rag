from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from math_rag.core.enums import IndexBuildStage, IndexBuildStatus


class IndexCreateResponse(BaseModel):
    id: UUID
    timestamp: datetime
    build_stage: IndexBuildStage
    build_status: IndexBuildStatus
