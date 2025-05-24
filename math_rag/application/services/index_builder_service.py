from logging import getLogger

from math_rag.application.base.repositories.documents import BaseIndexRepository
from math_rag.application.base.services import (
    BaseIndexBuilderService,
    BaseMathArticleLoaderService,
    BaseMathExpressionLabelLoaderService,
    BaseMathExpressionLoaderService,
)
from math_rag.application.enums.arxiv import MathCategory
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

    async def build(self, index: Index):
        if index.build_from_index_id:
            # TODO
            pass

        if index.build_from_stage:
            # TODO
            pass

        logger.info(f'Index {index.id} build started')

        await self.math_article_loader_service.load(MathCategory, 200)
        await self.index_repository.update_build_stage(
            index.id, IndexBuildStage.LOADED_MATH_ARTICLES
        )
        logger.info(f'Index {index.id} build loaded math articles')

        await self.math_expression_loader_service.load()
        await self.index_repository.update_build_stage(
            index.id, IndexBuildStage.LOADED_MATH_EXPRESSIONS
        )
        logger.info(f'Index {index.id} build loaded math expressions')

        await self.math_expression_label_loader_service.load()
        await self.index_repository.update_build_stage(
            index.id, IndexBuildStage.LOADED_MATH_EXPRESSION_LABELS
        )
        logger.info(f'Index {index.id} build loaded math expression labels')
        logger.info(f'Index {index.id} build finished')
