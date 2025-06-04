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
from math_rag.application.enums.arxiv import MathCategory
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

    async def _stage_0(self, dataset_id: UUID):
        logger.info(f'Dataset {dataset_id} build loading math articles...')

        # update build stage
        build_stage = MathExpressionDatasetBuildStage.LOAD_MATH_ARTICLES
        await self.math_expression_dataset_repository.update_build_stage(
            dataset_id, MathExpressionDatasetBuildStage.LOAD_MATH_ARTICLES
        )
        logger.info(f'Dataset {dataset_id} build stage updated to {build_stage}')

        # load
        # TODO
        await self.math_article_loader_service.load(
            dataset_id, arxiv_category_type=None, arxiv_category=MathCategory.GM, limit=1
        )
        logger.info(f'Dataset {dataset_id} build loaded math articles')

    async def _stage_1(self, dataset_id: UUID, build_from_dataset_id: UUID | None):
        logger.info(f'Dataset {dataset_id} build loading math expressions...')

        # update build stage
        build_stage = MathExpressionDatasetBuildStage.LOAD_MATH_EXPRESSIONS
        await self.math_expression_dataset_repository.update_build_stage(dataset_id, build_stage)
        logger.info(f'Dataset {dataset_id} build stage updated to {build_stage}')

        # load
        await self.math_expression_loader_service.load_for_dataset(
            dataset_id, build_from_dataset_id
        )
        logger.info(f'Dataset {dataset_id} build loaded math expressions')

    async def _stage_2(self, dataset_id: UUID, build_from_dataset_id: UUID | None):
        logger.info(f'Dataset {dataset_id} build loading math expression labels...')

        # update build stage
        build_stage = MathExpressionDatasetBuildStage.LOAD_MATH_EXPRESSION_LABELS
        await self.math_expression_dataset_repository.update_build_stage(
            dataset_id, MathExpressionDatasetBuildStage.LOAD_MATH_EXPRESSION_LABELS
        )
        logger.info(f'Dataset {dataset_id} build stage updated to {build_stage}')

        # load
        await self.math_expression_label_loader_service.load(dataset_id, build_from_dataset_id)
        logger.info(f'Dataset {dataset_id} build loaded math expression labels')

    async def _stage_3(self, dataset_id: UUID, build_from_dataset_id: UUID | None):
        logger.info(f'Dataset {dataset_id} build loading math expression samples...')

        # update build stage
        build_stage = MathExpressionDatasetBuildStage.LOAD_MATH_EXPRESSION_SAMPLES
        await self.math_expression_dataset_repository.update_build_stage(
            dataset_id, MathExpressionDatasetBuildStage.LOAD_MATH_EXPRESSION_SAMPLES
        )
        logger.info(f'Dataset {dataset_id} build stage updated to {build_stage}')

        # load
        await self.math_expression_sample_loader_service.load(dataset_id, build_from_dataset_id)
        logger.info(f'Dataset {dataset_id} build loaded math expression samples')

    async def _stage_4(self, dataset_id: UUID, build_from_dataset_id: UUID | None):
        logger.info(f'Dataset {dataset_id} publishing...')

        # publish
        await self.math_expression_dataset_publisher_service.publish(
            dataset_id, build_from_dataset_id
        )
        logger.info(f'Dataset {dataset_id} published')

    async def build(self, dataset: MathExpressionDataset):
        logger.info(f'Dataset {dataset.id} build started')

        if dataset.build_from_dataset_id and dataset.build_from_stage:
            build_from_dataset_exists = await self.math_expression_dataset_repository.exists(
                dataset.build_from_dataset_id
            )

            if not build_from_dataset_exists:
                raise ValueError(f'Dataset {dataset.build_from_dataset_id} does not exist')

            match dataset.build_from_stage:
                case MathExpressionDatasetBuildStage.LOAD_MATH_ARTICLES:
                    # NOTE: same as standard approach since it starts from the beginning
                    await self._stage_0(dataset.id)
                    await self._stage_1(dataset.id, None)
                    await self._stage_2(dataset.id, None)
                    await self._stage_3(dataset.id, None)
                    await self._stage_4(dataset.id, dataset.build_from_dataset_id)

                case MathExpressionDatasetBuildStage.LOAD_MATH_EXPRESSIONS:
                    await self._stage_1(dataset.id, dataset.build_from_dataset_id)
                    await self._stage_2(dataset.id, dataset.build_from_dataset_id)
                    await self._stage_3(dataset.id, dataset.build_from_dataset_id)
                    await self._stage_4(dataset.id, dataset.build_from_dataset_id)

                case MathExpressionDatasetBuildStage.LOAD_MATH_EXPRESSION_LABELS:
                    await self._stage_2(dataset.id, dataset.build_from_dataset_id)
                    await self._stage_3(dataset.id, dataset.build_from_dataset_id)
                    await self._stage_4(dataset.id, dataset.build_from_dataset_id)

                case MathExpressionDatasetBuildStage.LOAD_MATH_EXPRESSION_SAMPLES:
                    await self._stage_3(dataset.id, dataset.build_from_dataset_id)
                    await self._stage_4(dataset.id, dataset.build_from_dataset_id)

                case MathExpressionDatasetBuildStage.PUBLISH_MATH_EXPRESSION_DATASET:
                    await self._stage_4(dataset.id, dataset.build_from_dataset_id)

        else:
            await self._stage_0(dataset.id)
            await self._stage_1(dataset.id, None)
            await self._stage_2(dataset.id, None)
            await self._stage_3(dataset.id, None)
            await self._stage_4(dataset.id, dataset.build_from_dataset_id)

        logger.info(f'Dataset {dataset.id} build finished')
