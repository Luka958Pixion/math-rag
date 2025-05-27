from logging import getLogger
from uuid import UUID

from math_rag.application.base.repositories.documents import BaseDatasetRepository
from math_rag.application.base.services import (
    BaseDatasetBuilderService,
    BaseMathArticleLoaderService,
    BaseMathExpressionLabelLoaderService,
    BaseMathExpressionLoaderService,
)
from math_rag.application.enums.arxiv import BaseArxivCategory, MathCategory
from math_rag.core.enums import DatasetBuildStage
from math_rag.core.models import Dataset


logger = getLogger(__name__)


class DatasetBuilderService(BaseDatasetBuilderService):
    def __init__(
        self,
        math_article_loader_service: BaseMathArticleLoaderService,
        math_expression_loader_service: BaseMathExpressionLoaderService,
        math_expression_label_loader_service: BaseMathExpressionLabelLoaderService,
        dataset_repository: BaseDatasetRepository,
    ):
        self.math_article_loader_service = math_article_loader_service
        self.math_expression_loader_service = math_expression_loader_service
        self.math_expression_label_loader_service = math_expression_label_loader_service
        self.dataset_repository = dataset_repository

    async def _load_math_articles(
        self, dataset_id: UUID, arxiv_category_type: type[BaseArxivCategory], limit: int
    ):
        await self.dataset_repository.update_build_stage(
            dataset_id, DatasetBuildStage.LOAD_MATH_ARTICLES
        )
        await self.math_article_loader_service.load(
            dataset_id, arxiv_category_type, limit
        )
        logger.info(f'Dataset {dataset_id} build loaded math articles')

    async def _load_math_expressions(
        self, dataset_id: UUID, foundation_dataset_id: UUID | None
    ):
        await self.dataset_repository.update_build_stage(
            dataset_id, DatasetBuildStage.LOAD_MATH_EXPRESSIONS
        )
        await self.math_expression_loader_service.load(
            dataset_id, foundation_dataset_id
        )
        logger.info(f'Dataset {dataset_id} build loaded math expressions')

    async def _load_math_expression_labels(
        self, dataset_id: UUID, foundation_dataset_id: UUID | None
    ):
        await self.dataset_repository.update_build_stage(
            dataset_id, DatasetBuildStage.LOAD_MATH_EXPRESSION_LABELS
        )
        await self.math_expression_label_loader_service.load(
            dataset_id, foundation_dataset_id
        )
        logger.info(f'Dataset {dataset_id} build loaded math expression labels')

    async def _publish_math_expression_dataset(self):
        # TODO
        pass

    async def build(self, dataset: Dataset):
        logger.info(f'Dataset {dataset.id} build started')

        arxiv_category_type = MathCategory
        limit = 32  # TODO was 200

        if dataset.build_from_dataset_id and dataset.build_from_stage:
            foundation_dataset = await self.dataset_repository.find_one(
                filter={'id': dataset.build_from_dataset_id}
            )

            if not foundation_dataset:
                raise ValueError(
                    f'Dataset {dataset.build_from_dataset_id} does not exist'
                )

            match dataset.build_from_stage:
                case DatasetBuildStage.LOAD_MATH_ARTICLES:
                    # NOTE: same as standard approach since it starts from the beginning
                    await self._load_math_articles(
                        dataset.id, arxiv_category_type, limit
                    )
                    await self._load_math_expressions(dataset.id, None)
                    await self._load_math_expression_labels(dataset.id, None)

                case DatasetBuildStage.LOAD_MATH_EXPRESSIONS:
                    await self._load_math_expressions(dataset.id, foundation_dataset.id)
                    await self._load_math_expression_labels(
                        dataset.id, foundation_dataset.id
                    )

                case DatasetBuildStage.LOAD_MATH_EXPRESSION_LABELS:
                    await self._load_math_expression_labels(
                        dataset.id, foundation_dataset.id
                    )

        else:
            await self._load_math_articles(dataset.id, arxiv_category_type, limit)
            await self._load_math_expressions(dataset.id, None)
            await self._load_math_expression_labels(dataset.id, None)

        logger.info(f'Dataset {dataset.id} build finished')
