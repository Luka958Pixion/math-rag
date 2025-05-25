from uuid import UUID

from pydantic import BaseModel

from math_rag.core.enums import IndexBuildStage, IndexBuildStatus


class IndexCreateRequest(BaseModel):
    build_stage: IndexBuildStage
    build_status: IndexBuildStatus
    build_from_index_id: UUID | None
    build_from_stage: IndexBuildStage | None
