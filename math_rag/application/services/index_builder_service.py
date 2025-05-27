from logging import getLogger
from uuid import UUID

from math_rag.application.base.repositories.documents import BaseIndexRepository
from math_rag.application.base.services import (
    BaseIndexBuilderService,
    BaseMathArticleLoaderService,
    BaseMathExpressionLabelLoaderService,
    BaseMathExpressionLoaderService,
)
from math_rag.application.enums.arxiv import BaseArxivCategory, MathCategory
from math_rag.core.enums import IndexBuildStage
from math_rag.core.models import Index


logger = getLogger(__name__)


class IndexBuilderService(BaseIndexBuilderService):
    def __init__(
        self,
        math_article_loader_service: BaseMathArticleLoaderService,
        math_expression_loader_service: BaseMathExpressionLoaderService,
        math_expression_label_loader_service: BaseMathExpressionLabelLoaderService,
        index_repository: BaseIndexRepository,
    ):
        self.math_article_loader_service = math_article_loader_service
        self.math_expression_loader_service = math_expression_loader_service
        self.math_expression_label_loader_service = math_expression_label_loader_service
        self.index_repository = index_repository

    async def _load_math_articles(
        self, index_id: UUID, arxiv_category_type: type[BaseArxivCategory], limit: int
    ):
        await self.index_repository.update_build_stage(index_id, IndexBuildStage.LOAD_MATH_ARTICLES)
        await self.math_article_loader_service.load(index_id, arxiv_category_type, limit)
        logger.info(f'Index {index_id} build loaded math articles')

    async def _load_math_expressions(self, index_id: UUID, foundation_index_id: UUID | None):
        await self.index_repository.update_build_stage(
            index_id, IndexBuildStage.LOAD_MATH_EXPRESSIONS
        )
        await self.math_expression_loader_service.load(index_id, foundation_index_id)
        logger.info(f'Index {index_id} build loaded math expressions')

    async def _load_math_expression_labels(self, index_id: UUID, foundation_index_id: UUID | None):
        await self.index_repository.update_build_stage(
            index_id, IndexBuildStage.LOAD_MATH_EXPRESSION_LABELS
        )
        await self.math_expression_label_loader_service.load(index_id, foundation_index_id)
        logger.info(f'Index {index_id} build loaded math expression labels')

    async def build(self, index: Index):
        logger.info(f'Index {index.id} build started')

        arxiv_category_type = MathCategory
        limit = 32  # TODO was 200

        if index.build_from_index_id and index.build_from_stage:
            foundation_index = await self.index_repository.find_one(
                filter={'id': index.build_from_index_id}
            )

            if not foundation_index:
                raise ValueError(f'Index {index.build_from_index_id} does not exist')

            match index.build_from_stage:
                case IndexBuildStage.LOAD_MATH_ARTICLES:
                    # NOTE: same as standard approach since it starts from the beginning
                    await self._load_math_articles(index.id, arxiv_category_type, limit)
                    await self._load_math_expressions(index.id, None)
                    await self._load_math_expression_labels(index.id, None)

                case IndexBuildStage.LOAD_MATH_EXPRESSIONS:
                    await self._load_math_expressions(index.id, foundation_index.id)
                    await self._load_math_expression_labels(index.id, foundation_index.id)

                case IndexBuildStage.LOAD_MATH_EXPRESSION_LABELS:
                    await self._load_math_expression_labels(index.id, foundation_index.id)

        else:
            await self._load_math_articles(index.id, arxiv_category_type, limit)
            await self._load_math_expressions(index.id, None)
            await self._load_math_expression_labels(index.id, None)

        logger.info(f'Index {index.id} build finished')
