from uuid import UUID

from math_rag.application.base.repositories.documents import (
    BaseMathExpressionDatasetRepository,
    BaseTaskRepository,
)
from math_rag.application.base.services import BaseMathExpressionDatasetBuilderService
from math_rag.core.models import MathExpressionDataset

from .partials import PartialBackgroundService


class MathExpressionDatasetBackgroundService(PartialBackgroundService):
    def __init__(
        self,
        math_expression_dataset_builder_service: BaseMathExpressionDatasetBuilderService,
        math_expression_dataset_repository: BaseMathExpressionDatasetRepository,
        task_repository: BaseTaskRepository,
    ):
        super().__init__(task_repository)

        self.math_expression_dataset_builder_service = math_expression_dataset_builder_service
        self.math_expression_dataset_repository = math_expression_dataset_repository

    async def task(self, task_model_id: UUID):
        dataset = await self.math_expression_dataset_repository.find_one(
            filter=dict(id=task_model_id)
        )

        if not dataset:
            raise ValueError()

        await self.math_expression_dataset_builder_service.build(dataset)

    def task_model_name(self) -> str:
        return MathExpressionDataset.__name__
