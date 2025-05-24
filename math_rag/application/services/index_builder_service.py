from logging import getLogger

from math_rag.application.base.services import (
    BaseIndexBuilderService,
    BaseMathArticleLoaderService,
    BaseMathExpressionLabelLoaderService,
    BaseMathExpressionLoaderService,
)
from math_rag.core.models import Index


logger = getLogger(__name__)


class IndexBuilderService(BaseIndexBuilderService):
    def __init__(
        self,
        math_article_loader_service: BaseMathArticleLoaderService,
        math_expression_loader_service: BaseMathExpressionLoaderService,
        math_expression_label_loader_service: BaseMathExpressionLabelLoaderService,
    ):
        self.math_article_loader_service = math_article_loader_service
        self.math_expression_loader_service = math_expression_loader_service
        self.math_expression_label_loader_service = math_expression_label_loader_service

    async def build(index: Index):
        logger.info(f'Starting build for index {index.id}')
        # TODO build
        logger.info(f'Finished build for index {index.id}')
