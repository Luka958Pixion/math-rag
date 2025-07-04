from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .mm_params import MMParams
from .mm_router_params import MMRouterParams


class MMRequest(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    text: str
    params: MMParams
    router_params: MMRouterParams | None
