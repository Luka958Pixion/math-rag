from uuid import UUID

from pydantic import BaseModel

from math_rag.core.enums import IndexBuildStage


class IndexCreateRequest(BaseModel):
    build_from_index_id: UUID | None
    build_from_stage: IndexBuildStage | None
