from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.application.enums.inference import MMInferenceProvider, MMModelProvider


class MMRouterParams(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    inference_provider: MMInferenceProvider
    model_provider: MMModelProvider
