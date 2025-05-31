from logging import getLogger
from uuid import UUID

from math_rag.application.base.repositories.documents import BaseMathExpressionDatasetRepository
from math_rag.application.base.services import (
    BaseMathArticleLoaderService,
    BaseMathExpressionDatasetBuilderService,
    BaseMathExpressionDatasetPublisherService,
    BaseMathExpressionLabelLoaderService,
    BaseMathExpressionLoaderService,
    BaseMathExpressionSampleLoaderService,
)
from math_rag.application.enums.arxiv import BaseArxivCategory, MathCategory
from math_rag.core.enums import MathExpressionDatasetBuildStage
from math_rag.core.models import MathExpressionDataset


logger = getLogger(__name__)


class MathExpressionDatasetBuilderService(BaseMathExpressionDatasetBuilderService):
    def __init__(
        self,
        math_article_loader_service: BaseMathArticleLoaderService,
        math_expression_loader_service: BaseMathExpressionLoaderService,
        math_expression_label_loader_service: BaseMathExpressionLabelLoaderService,
        math_expression_sample_loader_service: BaseMathExpressionSampleLoaderService,
        math_expression_dataset_publisher_service: BaseMathExpressionDatasetPublisherService,
        math_expression_dataset_repository: BaseMathExpressionDatasetRepository,
    ):
        self.math_article_loader_service = math_article_loader_service
        self.math_expression_loader_service = math_expression_loader_service
        self.math_expression_label_loader_service = math_expression_label_loader_service
        self.math_expression_sample_loader_service = math_expression_sample_loader_service
        self.math_expression_dataset_publisher_service = math_expression_dataset_publisher_service
        self.math_expression_dataset_repository = math_expression_dataset_repository

    async def _load_math_articles(
        self, dataset_id: UUID, arxiv_category_type: type[BaseArxivCategory], limit: int
    ):
        await self.math_expression_dataset_repository.update_build_stage(
            dataset_id, MathExpressionDatasetBuildStage.LOAD_MATH_ARTICLES
        )
        await self.math_article_loader_service.load(dataset_id, arxiv_category_type, limit)
        logger.info(f'Dataset {dataset_id} build loaded math articles')

    async def _load_math_expressions(self, dataset_id: UUID, foundation_dataset_id: UUID | None):
        await self.math_expression_dataset_repository.update_build_stage(
            dataset_id, MathExpressionDatasetBuildStage.LOAD_MATH_EXPRESSIONS
        )
        await self.math_expression_loader_service.load(dataset_id, foundation_dataset_id)
        logger.info(f'Dataset {dataset_id} build loaded math expressions')

    async def _load_math_expression_labels(
        self, dataset_id: UUID, foundation_dataset_id: UUID | None
    ):
        await self.math_expression_dataset_repository.update_build_stage(
            dataset_id, MathExpressionDatasetBuildStage.LOAD_MATH_EXPRESSION_LABELS
        )
        await self.math_expression_label_loader_service.load(dataset_id, foundation_dataset_id)
        logger.info(f'Dataset {dataset_id} build loaded math expression labels')

    async def _load_math_expression_samples(
        self, dataset_id: UUID, foundation_dataset_id: UUID | None
    ):
        await self.math_expression_dataset_repository.update_build_stage(
            dataset_id, MathExpressionDatasetBuildStage.LOAD_MATH_EXPRESSION_SAMPLES
        )
        await self.math_expression_sample_loader_service.load(dataset_id, foundation_dataset_id)
        logger.info(f'Dataset {dataset_id} build loaded math expression samples')

    async def _publish_math_expression_dataset(self, dataset: MathExpressionDataset):
        await self.math_expression_dataset_publisher_service.publish(dataset)
        logger.info(f'Dataset {dataset.id} published')

    async def build(self, dataset: MathExpressionDataset):
        logger.info(f'Dataset {dataset.id} build started')

        arxiv_category_type = MathCategory
        limit = 32  # TODO was 200

        if dataset.build_from_dataset_id and dataset.build_from_stage:
            foundation_dataset = await self.math_expression_dataset_repository.find_one(
                filter={'id': dataset.build_from_dataset_id}
            )

            if not foundation_dataset:
                raise ValueError(f'Dataset {dataset.build_from_dataset_id} does not exist')

            match dataset.build_from_stage:
                case MathExpressionDatasetBuildStage.LOAD_MATH_ARTICLES:
                    # NOTE: same as standard approach since it starts from the beginning
                    await self._load_math_articles(dataset.id, arxiv_category_type, limit)
                    await self._load_math_expressions(dataset.id, None)
                    await self._load_math_expression_labels(dataset.id, None)
                    await self._load_math_expression_samples(dataset.id, None)
                    await self._publish_math_expression_dataset(dataset)

                case MathExpressionDatasetBuildStage.LOAD_MATH_EXPRESSIONS:
                    await self._load_math_expressions(dataset.id, foundation_dataset.id)
                    await self._load_math_expression_labels(dataset.id, foundation_dataset.id)
                    await self._load_math_expression_samples(dataset.id, foundation_dataset.id)
                    await self._publish_math_expression_dataset(dataset)

                case MathExpressionDatasetBuildStage.LOAD_MATH_EXPRESSION_LABELS:
                    await self._load_math_expression_labels(dataset.id, foundation_dataset.id)
                    await self._load_math_expression_samples(dataset.id, foundation_dataset.id)
                    await self._publish_math_expression_dataset(dataset)

        else:
            await self._load_math_articles(dataset.id, arxiv_category_type, limit)
            await self._load_math_expressions(dataset.id, None)
            await self._load_math_expression_labels(dataset.id, None)
            await self._load_math_expression_samples(dataset.id, None)
            await self._publish_math_expression_dataset(dataset)

        logger.info(f'Dataset {dataset.id} build finished')
