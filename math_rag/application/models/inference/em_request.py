from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .em_params import EMParams
from .em_router_params import EMRouterParams


class EMRequest(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    text: str
    params: EMParams
    router_params: EMRouterParams | None
