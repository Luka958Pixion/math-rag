from logging import getLogger
from typing import Awaitable, Callable
from uuid import UUID

from math_rag.application.base.repositories.documents import BaseMathExpressionIndexRepository
from math_rag.application.base.services import (
    BaseMathExpressionIndexBuilderService,
)
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

    async def search(self, index_id: UUID, query: str, *, limit: int) -> list[UUID]:
        logger.info(f'Index {index_id} search started')

        logger.info(f'Index {index_id} search finished')
