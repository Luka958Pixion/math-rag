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
from math_rag.application.models.assistants import (
    MathExpressionLabelerAssistantInput,
    MathExpressionLabelerAssistantOutput,
)
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

    async def load(self, index_id: UUID, foundation_index_id: UUID | None):
        num_math_expression_labels = 0

        async for batch in self.math_expression_repository.batch_find_many(
            batch_size=1000,
            filter={'id': foundation_index_id if foundation_index_id else index_id},
        ):
            for math_expression in batch:
                # TODO
                input = MathExpressionLabelerAssistantInput(latex=math_expression.latex)
                output = await self.math_expression_labeler_assistant.assist(input)

                math_expression_label = MathExpressionLabel(
                    index_id=index_id,
                    math_expression_id=math_expression.id,
                    value=output.label,
                )

                await self.math_expression_label_repository.insert_many(
                    [math_expression_label]
                )

        await self.math_expression_label_repository.backup()
        logger.info(
            f'{self.__class__.__name__} loaded {num_math_expression_labels} math expression labels'
        )
