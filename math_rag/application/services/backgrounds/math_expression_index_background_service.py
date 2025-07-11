from uuid import UUID

from math_rag.application.base.repositories.documents import (
    BaseMathExpressionIndexRepository,
    BaseTaskRepository,
)
from math_rag.application.base.services import BaseMathExpressionIndexBuilderService
from math_rag.core.models import MathExpressionIndex

from .partials import PartialTaskBackgroundService


class MathExpressionIndexBackgroundService(PartialTaskBackgroundService):
    def __init__(
        self,
        math_expression_index_builder_service: BaseMathExpressionIndexBuilderService,
        math_expression_index_repository: BaseMathExpressionIndexRepository,
        task_repository: BaseTaskRepository,
    ):
        super().__init__(task_repository)

        self.math_expression_index_builder_service = math_expression_index_builder_service
        self.math_expression_index_repository = math_expression_index_repository

    async def task(self, task_model_id: UUID):
        index = await self.math_expression_index_repository.find_one(filter=dict(id=task_model_id))

        if not index:
            raise ValueError()

        await self.math_expression_index_builder_service.build(index)

    def task_model_name(self) -> str:
        return MathExpressionIndex.__name__
