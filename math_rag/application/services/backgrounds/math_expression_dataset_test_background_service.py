from uuid import UUID

from math_rag.application.base.repositories.documents import (
    BaseMathExpressionDatasetTestRepository,
    BaseMathExpressionDatasetTestResultRepository,
    BaseTaskRepository,
)
from math_rag.application.base.services import BaseMathExpressionDatasetTesterService
from math_rag.core.models import MathExpressionDatasetTest

from .partials import PartialTaskBackgroundService


class MathExpressionDatasetTestBackgroundService(PartialTaskBackgroundService):
    def __init__(
        self,
        math_expression_dataset_tester_service: BaseMathExpressionDatasetTesterService,
        math_expression_dataset_test_repository: BaseMathExpressionDatasetTestRepository,
        math_expression_dataset_test_result_repository: BaseMathExpressionDatasetTestResultRepository,
        task_repository: BaseTaskRepository,
    ):
        super().__init__(task_repository)

        self.math_expression_dataset_tester_service = math_expression_dataset_tester_service
        self.math_expression_dataset_test_result_repository = (
            math_expression_dataset_test_result_repository
        )
        self.math_expression_dataset_test_repository = math_expression_dataset_test_repository

    async def task(self, task_model_id: UUID):
        test = await self.math_expression_dataset_test_repository.find_one(
            filter=dict(id=task_model_id)
        )

        if not test:
            raise ValueError()

        result = await self.math_expression_dataset_tester_service.test(test)
        await self.math_expression_dataset_test_result_repository.insert_one(result)

    def task_model_name(self) -> str:
        return MathExpressionDatasetTest.__name__
