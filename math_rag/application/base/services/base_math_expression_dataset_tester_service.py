from abc import ABC, abstractmethod
from uuid import UUID

from math_rag.application.enums.inference import LLMInferenceProvider, LLMModelProvider
from math_rag.core.models import MathExpressionLabel


class BaseMathExpressionDatasetTesterService(ABC):
    @abstractmethod
    async def test(
        self,
        dataset_id: UUID,
        model: str,
        inference_provider: LLMInferenceProvider,
        model_provider: LLMModelProvider,
    ) -> list[MathExpressionLabel]:
        pass
