from logging import getLogger
from uuid import UUID

from math_rag.application.base.repositories.documents import BaseIndexRepository
from math_rag.application.base.services import (
    BaseIndexBuilderService,
    BaseMathArticleLoaderService,
    BaseMathExpressionLabelLoaderService,
    BaseMathExpressionLoaderService,
)
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

    async def _stage_0(self, index_id: UUID):
        logger.info(f'Index {index_id} build loading math expressions...')

        # update build stage
        build_stage = IndexBuildStage.LOAD_MATH_EXPRESSIONS
        await self.index_repository.update_build_stage(index_id, build_stage)
        logger.info(f'Index {index_id} build stage updated to {build_stage}')

        # load
        await self.math_expression_loader_service.load_for_index(index_id)
        logger.info(f'Index {index_id} build loaded math expressions')

    async def _stage_1(self, index_id: UUID):
        logger.info(f'Index {index_id} build loading math expression labels...')

        # update build stage
        build_stage = IndexBuildStage.LOAD_MATH_EXPRESSION_LABELS
        await self.index_repository.update_build_stage(index_id, build_stage)
        logger.info(f'Index {index_id} build stage updated to {build_stage}')

        # load
        await self.math_expression_label_loader_service.load(index_id)
        logger.info(f'Index {index_id} build loaded math expression labels')

    async def build(self, index: Index):
        logger.info(f'Index {index.id} build started')

        await self._stage_0(index.id)
        await self._stage_1(index.id)

        logger.info(f'Index {index.id} build finished')
