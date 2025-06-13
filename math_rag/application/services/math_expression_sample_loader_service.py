from logging import getLogger

from math_rag.application.base.repositories.documents import BaseMathExpressionSampleRepository
from math_rag.application.base.services import BaseMathExpressionSampleLoaderService
from math_rag.core.models import MathExpressionDataset


logger = getLogger(__name__)


class MathExpressionSampleLoaderService(BaseMathExpressionSampleLoaderService):
    def __init__(
        self,
        math_expression_sample_repository: BaseMathExpressionSampleRepository,
    ):
        self.math_expression_sample_repository = math_expression_sample_repository

    async def load(self, dataset: MathExpressionDataset):
        await self.math_expression_sample_repository.aggregate_and_batch_insert_many(
            dataset.build_from_id if dataset.build_from_id else dataset.id, batch_size=1000
        )

        await self.math_expression_sample_repository.backup()
        num_math_expression_samples = await self.math_expression_sample_repository.count(
            filter={'math_expression_dataset_id': dataset.id}
        )
        logger.info(
            f'{self.__class__.__name__} loaded {num_math_expression_samples} math expression samples'
        )
