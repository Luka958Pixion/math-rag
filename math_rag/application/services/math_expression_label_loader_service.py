from logging import getLogger
from uuid import UUID

from math_rag.application.assistants import MathExpressionLabelerAssistant
from math_rag.application.base.repositories.documents import (
    BaseMathExpressionLabelRepository,
    BaseMathExpressionRepository,
)
from math_rag.application.base.services import (
    BaseMathExpressionLabelLoaderService,
)
from math_rag.application.models.assistants import MathExpressionLabelerAssistantInput
from math_rag.core.models import MathExpressionLabel


logger = getLogger(__name__)


class MathExpressionLabelLoaderService(BaseMathExpressionLabelLoaderService):
    def __init__(
        self,
        math_expression_labeler_assistant: MathExpressionLabelerAssistant,
        math_expression_repository: BaseMathExpressionRepository,
        math_expression_label_repository: BaseMathExpressionLabelRepository,
    ):
        self.math_expression_labeler_assistant = math_expression_labeler_assistant
        self.math_expression_repository = math_expression_repository
        self.math_expression_label_repository = math_expression_label_repository

    async def load(self, dataset_id: UUID, foundation_dataset_id: UUID | None):
        num_math_expression_labels = 0

        inputs: list[MathExpressionLabelerAssistantInput] = []

        async for math_expressions in self.math_expression_repository.batch_find_many(
            batch_size=1000,
            filter={'id': foundation_dataset_id if foundation_dataset_id else dataset_id},
        ):
            for math_expression in math_expressions:
                input = MathExpressionLabelerAssistantInput(latex=math_expression.latex)
                inputs.append(input)

        outputs = await self.math_expression_labeler_assistant.batch_assist(
            inputs, use_scheduler=True
        )
        math_expression_labels = [
            MathExpressionLabel(
                math_expression_id=math_expression.id,
                math_expression_dataset_id=dataset_id,
                value=output.label,
            )
            for output in outputs
        ]

        await self.math_expression_label_repository.batch_insert_many(
            math_expression_labels, batch_size=1000
        )
        await self.math_expression_label_repository.backup()
        logger.info(
            f'{self.__class__.__name__} loaded {num_math_expression_labels} math expression labels'
        )
