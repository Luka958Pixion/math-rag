from logging import getLogger

from math_rag.application.base.repositories.documents import (
    BaseMathArticleChunkRepository,
    BaseMathExpressionRepository,
)
from math_rag.application.base.repositories.objects import BaseMathArticleRepository
from math_rag.application.base.services import (
    BaseMathArticleChunkLoaderService,
    BaseMathArticleParserService,
)
from math_rag.core.models import MathArticleChunk, MathExpressionIndex
from math_rag.infrastructure.utils import (
    TemplateChunkerUtil,
    TemplateFormatterUtil,
    TemplateIndexFinderUtil,
)


logger = getLogger(__name__)


class MathArticleChunkLoaderService(BaseMathArticleChunkLoaderService):
    def __init__(
        self,
        math_article_parser_service: BaseMathArticleParserService,
        math_article_repository: BaseMathArticleRepository,
        math_article_chunk_repository: BaseMathArticleChunkRepository,
        math_expression_repository: BaseMathExpressionRepository,
    ):
        self.math_article_parser_service = math_article_parser_service
        self.math_article_repository = math_article_repository
        self.math_article_chunk_repository = math_article_chunk_repository
        self.math_expression_repository = math_expression_repository

    async def load_for_index(self, index: MathExpressionIndex):
        index_filter = dict(math_expression_index_id=index.id)

        # math article
        math_article = await self.math_article_repository.find_by_math_expression_index_id(index.id)

        if not math_article:
            raise ValueError(f'Math article with index id {index.id} does not exist')

        _, _, template = self.math_article_parser_service.parse_for_index(math_article)

        # math expressions
        math_expressions = await self.math_expression_repository.find_many(filter=index_filter)

        # math article chunks
        index_to_katex = {
            math_expression.index: math_expression.katex for math_expression in math_expressions
        }
        chunk_templates = TemplateChunkerUtil.chunk(template, max_window_size=2048, max_padding=256)
        math_article_chunks: list[MathArticleChunk] = []

        for i, chunk_template in enumerate(chunk_templates):
            indexes = TemplateIndexFinderUtil.find(chunk_template)
            formatted_chunk, _ = TemplateFormatterUtil.format(
                chunk_template, index_to_katex, omit_wrapper=False
            )
            math_article_chunk = MathArticleChunk(
                math_article_id=math_article.id,
                math_expression_index_id=index.id,
                index=i,
                indexes=indexes,
                text=formatted_chunk,
            )
            math_article_chunks.append(math_article_chunk)

        await self.math_article_chunk_repository.insert_many(math_article_chunks)
        logger.info(
            f'{self.__class__.__name__} loaded {len(math_article_chunks)} math article chunks'
        )
