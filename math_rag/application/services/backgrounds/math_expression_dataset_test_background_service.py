from uuid import UUID

from math_rag.application.base.repositories.documents import (
    BaseMathExpressionDatasetTestRepository,
    BaseTaskRepository,
)
from math_rag.application.base.services import BaseMathExpressionDatasetTesterService
from math_rag.application.enums.inference import LLMInferenceProvider, LLMModelProvider
from math_rag.core.models import MathExpressionDatasetTest
from math_rag.shared.utils import TypeUtil

from .partials import PartialBackgroundService


class MathExpressionDatasetTestBackgroundService(PartialBackgroundService):
    def __init__(
        self,
        math_expression_dataset_tester_service: BaseMathExpressionDatasetTesterService,
        math_expression_dataset_test_repository: BaseMathExpressionDatasetTestRepository,
        task_repository: BaseTaskRepository,
    ):
        super().__init__(task_repository)

        self.math_expression_dataset_tester_service = math_expression_dataset_tester_service
        self.math_expression_dataset_test_repository = math_expression_dataset_test_repository

    async def task(self, task_model_id: UUID):
        test = await self.math_expression_dataset_test_repository.find_one(
            filter=dict(id=task_model_id)
        )

        if not test:
            raise ValueError()

        await self.math_expression_dataset_tester_service.test(
            dataset_id=test.math_expression_dataset_id,
            model=test.model,
            inference_provider=LLMInferenceProvider(test.inference_provider),
            model_provider=LLMModelProvider(test.model_provider),
        )

    def task_model_type(self) -> str:
        return TypeUtil.to_fqn(MathExpressionDatasetTest)
