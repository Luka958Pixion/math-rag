from uuid import UUID, uuid4

from pydantic import BaseModel, Field

from math_rag.application.enums.inference import LLMInferenceProvider, LLMModelProvider


class LLMRouterParams(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    inference_provider: LLMInferenceProvider | None
    model_provider: LLMModelProvider | None
