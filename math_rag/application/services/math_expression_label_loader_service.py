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
                pass  # TODO math_expression is Any

        await self.math_expression_label_repository.backup()
        logger.info(
            f'{self.__class__.__name__} loaded {num_math_expression_labels} math expression labels'
        )
