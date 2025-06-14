from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.application.enums.inference import EMInferenceProvider, EMProvider


class EMParams(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    model: str
    dimensions: int | None = None

    # NOTE: additional parameters that are not used during inference
    inference_provider: EMInferenceProvider
    model_provider: EMProvider
