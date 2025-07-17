from logging import getLogger

from math_rag.application.base.repositories.documents import (
    BaseMathExpressionContextRepository,
    BaseMathExpressionRepository,
)
from math_rag.application.base.repositories.objects import BaseMathArticleRepository
from math_rag.application.base.services import (
    BaseMathArticleParserService,
    BaseMathExpressionContextLoaderService,
)
from math_rag.core.models import MathExpressionContext, MathExpressionIndex
from math_rag.infrastructure.utils import (
    TemplateContextChunkerUtil,
    TemplateFormatterUtil,
)


logger = getLogger(__name__)


class MathExpressionContextLoaderService(BaseMathExpressionContextLoaderService):
    def __init__(
        self,
        math_article_parser_service: BaseMathArticleParserService,
        math_article_repository: BaseMathArticleRepository,
        math_expression_repository: BaseMathExpressionRepository,
        math_expression_context_repository: BaseMathExpressionContextRepository,
    ):
        self.math_article_parser_service = math_article_parser_service
        self.math_article_repository = math_article_repository
        self.math_expression_repository = math_expression_repository
        self.math_expression_context_repository = math_expression_context_repository

    async def load_for_index(self, index: MathExpressionIndex):
        index_filter = dict(math_expression_index_id=index.id)

        # math article
        math_article = await self.math_article_repository.find_by_math_expression_index_id(index.id)

        if not math_article:
            raise ValueError(f'Math article with index id {index.id} does not exist')

        _, _, template = self.math_article_parser_service.parse_for_index(math_article)
        context_templates = TemplateContextChunkerUtil.chunk(template, max_context_size=1000)

        # math expressions
        math_expressions = await self.math_expression_repository.find_many(filter=index_filter)
        math_expressions.sort(key=lambda x: x.index)
        index_to_katex = {
            math_expression.index: math_expression.katex for math_expression in math_expressions
        }

        # math expression contexts
        math_expression_contexts: list[MathExpressionContext] = []

        for math_expression, context_template in zip(math_expressions, context_templates):
            formatted_context, _ = TemplateFormatterUtil.format(
                context_template, index_to_katex, omit_wrapper=False
            )
            math_expression_context = MathExpressionContext(
                math_article_id=math_article.id,
                math_expression_id=math_expression.id,
                math_expression_index_id=index.id,
                text=formatted_context,
            )
            math_expression_contexts.append(math_expression_context)

        await self.math_expression_context_repository.insert_many(math_expression_contexts)
        logger.info(
            f'{self.__class__.__name__} loaded {len(math_expression_contexts)} math expression contexts'
        )
