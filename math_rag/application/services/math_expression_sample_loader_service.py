from logging import getLogger
from uuid import UUID

from math_rag.application.base.repositories.documents import BaseMathExpressionSampleRepository
from math_rag.application.base.services import BaseMathExpressionSampleLoaderService


logger = getLogger(__name__)


class MathExpressionSampleLoaderService(BaseMathExpressionSampleLoaderService):
    def __init__(
        self,
        math_expression_sample_repository: BaseMathExpressionSampleRepository,
    ):
        self.math_expression_sample_repository = math_expression_sample_repository

    async def load(self, dataset_id: UUID, build_from_dataset_id: UUID | None):
        await self.math_expression_sample_repository.aggregate_and_batch_insert_many(
            build_from_dataset_id if build_from_dataset_id else dataset_id, batch_size=1000
        )

        await self.math_expression_sample_repository.backup()
        num_math_expression_samples = await self.math_expression_sample_repository.count(
            filter={'math_expression_dataset_id': dataset_id}
        )
        logger.info(
            f'{self.__class__.__name__} loaded {num_math_expression_samples} math expression labels'
        )
