from uuid import UUID

from pydantic import BaseModel

from math_rag.core.enums import IndexBuildStage


class IndexCreateRequest(BaseModel):
    pass
