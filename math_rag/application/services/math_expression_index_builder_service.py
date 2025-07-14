from logging import getLogger
from typing import Awaitable, Callable
from uuid import UUID

from math_rag.application.base.repositories.documents import BaseMathExpressionIndexRepository
from math_rag.application.base.services import (
    BaseMathArticleChunkLoaderService,
    BaseMathArticleLoaderService,
    BaseMathExpressionContextLoaderService,
    BaseMathExpressionDescriptionLoaderService,
    BaseMathExpressionDescriptionOptLoaderService,
    BaseMathExpressionGroupLoaderService,
    BaseMathExpressionGroupRelationshipLoaderService,
    BaseMathExpressionIndexBuilderService,
    BaseMathExpressionLabelLoaderService,
    BaseMathExpressionLoaderService,
    BaseMathExpressionRelationshipDescriptionLoaderService,
    BaseMathExpressionRelationshipLoaderService,
)
from math_rag.core.enums import MathExpressionIndexBuildStage
from math_rag.core.models import MathExpressionIndex


logger = getLogger(__name__)


class MathExpressionIndexBuilderService(BaseMathExpressionIndexBuilderService):
    def __init__(
        self,
        math_article_chunk_loader_service: BaseMathArticleChunkLoaderService,
        math_article_loader_service: BaseMathArticleLoaderService,
        math_expression_context_loader_service: BaseMathExpressionContextLoaderService,
        math_expression_description_loader_service: BaseMathExpressionDescriptionLoaderService,
        math_expression_description_opt_loader_service: BaseMathExpressionDescriptionOptLoaderService,
        math_expression_group_loader_service: BaseMathExpressionGroupLoaderService,
        math_expression_group_relationship_loader_service: BaseMathExpressionGroupRelationshipLoaderService,
        math_expression_label_loader_service: BaseMathExpressionLabelLoaderService,
        math_expression_loader_service: BaseMathExpressionLoaderService,
        math_expression_relationship_description_loader_service: BaseMathExpressionRelationshipDescriptionLoaderService,
        math_expression_relationship_loader_service: BaseMathExpressionRelationshipLoaderService,
        math_expression_index_repository: BaseMathExpressionIndexRepository,
    ):
        self.math_article_chunk_loader_service = math_article_chunk_loader_service
        self.math_article_loader_service = math_article_loader_service
        self.math_expression_context_loader_service = math_expression_context_loader_service
        self.math_expression_description_loader_service = math_expression_description_loader_service
        self.math_expression_description_opt_loader_service = (
            math_expression_description_opt_loader_service
        )
        self.math_expression_group_loader_service = math_expression_group_loader_service
        self.math_expression_group_relationship_loader_service = (
            math_expression_group_relationship_loader_service
        )
        self.math_expression_label_loader_service = math_expression_label_loader_service
        self.math_expression_loader_service = math_expression_loader_service
        self.math_expression_relationship_description_loader_service = (
            math_expression_relationship_description_loader_service
        )
        self.math_expression_relationship_loader_service = (
            math_expression_relationship_loader_service
        )
        self.math_expression_index_repository = math_expression_index_repository

        # (build stage, loader service, description)
        self._stages = [
            (
                MathExpressionIndexBuildStage.LOAD_MATH_ARTICLES,
                self.math_article_loader_service.load_for_index,
                'math articles',
            ),
            (
                MathExpressionIndexBuildStage.LOAD_MATH_EXPRESSIONS,
                self.math_expression_loader_service.load_for_index,
                'math expressions',
            ),
            (
                MathExpressionIndexBuildStage.LOAD_MATH_EXPRESSION_LABELS,
                self.math_expression_label_loader_service.load_for_index,
                'math expression labels',
            ),
            (
                MathExpressionIndexBuildStage.LOAD_MATH_EXPRESSION_CONTEXTS,
                self.math_expression_context_loader_service.load_for_index,
                'math expression contexts',
            ),
            (
                MathExpressionIndexBuildStage.LOAD_MATH_EXPRESSION_DESCRIPTIONS,
                self.math_expression_description_loader_service.load_for_index,
                'math expression descriptions',
            ),
            (
                MathExpressionIndexBuildStage.LOAD_MATH_EXPRESSION_DESCRIPTION_OPTS,
                self.math_expression_description_opt_loader_service.load_for_index,
                'math expression description opts',
            ),
            (
                MathExpressionIndexBuildStage.LOAD_MATH_EXPRESSION_GROUPS,
                self.math_expression_group_loader_service.load_for_index,
                'math expression groups',
            ),
            (
                MathExpressionIndexBuildStage.LOAD_MATH_EXPRESSION_GROUP_RELATIONSHIPS,
                self.math_expression_group_relationship_loader_service.load_for_index,
                'math expression group relationships',
            ),
            (
                MathExpressionIndexBuildStage.LOAD_MATH_ARTICLE_CHUNKS,
                self.math_article_chunk_loader_service.load_for_index,
                'math article chunks',
            ),
            (
                MathExpressionIndexBuildStage.LOAD_MATH_EXPRESSION_RELATIONSHIPS,
                self.math_expression_relationship_loader_service.load_for_index,
                'math expression relationships',
            ),
            (
                MathExpressionIndexBuildStage.LOAD_MATH_EXPRESSION_RELATIONSHIP_DESCRIPTIONS,
                self.math_expression_relationship_description_loader_service.load_for_index,
                'math expression relationship descriptions',
            ),
        ]

    async def _run_stage(
        self,
        index: MathExpressionIndex,
        stage_enum: MathExpressionIndexBuildStage,
        load_method: Callable[[UUID], Awaitable],
        description: str,
    ):
        logger.info(f'Index {index.id} build loading {description}...')

        # update build stage
        await self.math_expression_index_repository.update_build_stage(index.id, stage_enum)
        logger.info(f'Index {index.id} build stage updated to {stage_enum}')

        # load
        await load_method(index.id)
        logger.info(f'Index {index.id} build loaded {description}')

    async def build(self, index: MathExpressionIndex):
        logger.info(f'Index {index.id} build started')

        for build_stage, load_method, description in self._stages:
            await self._run_stage(index, build_stage, load_method, description)

        logger.info(f'Index {index.id} build finished')
