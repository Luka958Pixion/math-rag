from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from .em_params import EMParams


class EMRequest(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    text: str
    params: EMParams
