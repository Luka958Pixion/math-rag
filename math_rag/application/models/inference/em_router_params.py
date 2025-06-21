from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.application.enums.inference import EMInferenceProvider, EMModelProvider


class EMRouterParams(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    inference_provider: EMInferenceProvider
    model_provider: EMModelProvider
