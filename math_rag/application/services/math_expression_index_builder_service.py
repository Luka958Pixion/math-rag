from logging import getLogger

from math_rag.application.base.repositories.documents import BaseMathExpressionIndexRepository
from math_rag.application.base.services import (
    BaseMathArticleLoaderService,
    BaseMathExpressionIndexBuilderService,
    BaseMathExpressionLabelLoaderService,
    BaseMathExpressionLoaderService,
)
from math_rag.core.enums import MathExpressionIndexBuildStage
from math_rag.core.models import MathExpressionIndex


logger = getLogger(__name__)


class MathExpressionIndexBuilderService(BaseMathExpressionIndexBuilderService):
    def __init__(
        self,
        math_article_loader_service: BaseMathArticleLoaderService,
        math_expression_loader_service: BaseMathExpressionLoaderService,
        math_expression_label_loader_service: BaseMathExpressionLabelLoaderService,
        math_expression_index_repository: BaseMathExpressionIndexRepository,
    ):
        self.math_article_loader_service = math_article_loader_service
        self.math_expression_loader_service = math_expression_loader_service
        self.math_expression_label_loader_service = math_expression_label_loader_service
        self.math_expression_index_repository = math_expression_index_repository

    async def _stage_0(self, index: MathExpressionIndex):
        logger.info(f'Index {index.id} build loading math expressions...')

        # update build stage
        build_stage = MathExpressionIndexBuildStage.LOAD_MATH_EXPRESSIONS
        await self.math_expression_index_repository.update_build_stage(index.id, build_stage)
        logger.info(f'Index {index.id} build stage updated to {build_stage}')

        # load
        await self.math_expression_loader_service.load_for_index(index.id)
        logger.info(f'Index {index.id} build loaded math expressions')

    async def _stage_1(self, index: MathExpressionIndex):
        logger.info(f'Index {index.id} build loading math expression labels...')

        # update build stage
        build_stage = MathExpressionIndexBuildStage.LOAD_MATH_EXPRESSION_LABELS
        await self.math_expression_index_repository.update_build_stage(index.id, build_stage)
        logger.info(f'Index {index.id} build stage updated to {build_stage}')

        # load
        await self.math_expression_label_loader_service.load_for_index(index.id)
        logger.info(f'Index {index.id} build loaded math expression labels')

    async def build(self, index: MathExpressionIndex):
        logger.info(f'Index {index.id} build started')

        await self._stage_0(index)
        await self._stage_1(index)

        logger.info(f'Index {index.id} build finished')
