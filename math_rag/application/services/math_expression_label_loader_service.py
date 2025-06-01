from logging import getLogger
from uuid import UUID

from math_rag.application.assistants import MathExpressionLabelerAssistant
from math_rag.application.base.repositories.documents import (
    BaseMathExpressionLabelRepository,
    BaseMathExpressionRepository,
)
from math_rag.application.base.services import BaseMathExpressionLabelLoaderService
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

    async def load(self, dataset_id: UUID, build_from_dataset_id: UUID | None):
        inputs: list[MathExpressionLabelerAssistantInput] = []
        input_id_to_math_expression_id: dict[UUID, UUID] = {}

        async for math_expressions in self.math_expression_repository.batch_find_many(
            batch_size=1000,
            filter={
                'math_expression_dataset_id': build_from_dataset_id
                if build_from_dataset_id
                else dataset_id
            },
        ):
            for math_expression in math_expressions:
                input = MathExpressionLabelerAssistantInput(latex=math_expression.latex)
                inputs.append(input)
                input_id_to_math_expression_id[input.id] = math_expression.id

        # outputs = await self.math_expression_labeler_assistant.batch_assist(
        #     inputs, use_scheduler=True
        # )
        # TODO bring back
        outputs = await self.math_expression_labeler_assistant.concurrent_assist(inputs)

        math_expression_labels = [
            MathExpressionLabel(
                math_expression_id=input_id_to_math_expression_id[output.input_id],
                math_expression_dataset_id=dataset_id,
                index_id=None,
                value=output.label,
            )
            for output in outputs
        ]
        await self.math_expression_label_repository.batch_insert_many(
            math_expression_labels, batch_size=1000
        )
        await self.math_expression_label_repository.backup()
        logger.info(
            f'{self.__class__.__name__} loaded {len(math_expression_labels)} math expression labels'
        )
